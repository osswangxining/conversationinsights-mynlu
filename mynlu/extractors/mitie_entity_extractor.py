from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import range, str
import logging
import os

import typing
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Text

from mynlu.config.mynluconfig import MyNLUConfig
from mynlu.extractors import EntityExtractor
from mynlu.model import Metadata
from mynlu.trainers import Message
from mynlu.trainers import TrainingData

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    import mitie


class MitieEntityExtractor(EntityExtractor):
    name = "ner_mitie"

    provides = ["entities"]

    requires = ["tokens"]

    def __init__(self, ner=None):
        self.ner = ner

    @classmethod
    def required_packages(cls):
        # type: () -> List[Text]
        return ["mitie"]

    def extract_entities(self, text, tokens, feature_extractor):
        extracted_entities = []
        tokens_strs = [token.text for token in tokens]
        if self.ner:
            entities = self.ner.extract_entities(tokens_strs, feature_extractor)
            for e in entities:
                if len(e[0]):
                    start = tokens[e[0][0]].offset
                    end = tokens[e[0][-1]].end

                    extracted_entities.append({
                        "entity": e[1],
                        "value": text[start:end],
                        "start": start,
                        "end": end
                    })

        return extracted_entities

    @staticmethod
    def find_entity(entity, text, tokens):
        offsets = [token.offset for token in tokens]
        ends = [token.end for token in tokens]
        if entity["start"] not in offsets:
            message = "Invalid entity {} in example '{}': entities must span whole tokens. Wrong entity start.".format(
                entity, text)
            raise ValueError(message)
        if entity["end"] not in ends:
            message = "Invalid entity {} in example '{}': entities must span whole tokens. Wrong entity end.".format(
                entity, text)
            raise ValueError(message)
        start = offsets.index(entity["start"])
        end = ends.index(entity["end"]) + 1
        return start, end

    def train(self, training_data, config, **kwargs):
        # type: (TrainingData, MyNLUConfig) -> None
        import mitie

        trainer = mitie.ner_trainer(config["mitie_file"])
        trainer.num_threads = config["num_threads"]
        found_one_entity = False
        for example in training_data.entity_examples:
            text = example.text
            tokens = example.get("tokens")
            sample = mitie.ner_training_instance([t.text for t in tokens])
            for ent in example.get("entities", []):
                try:
                    start, end = MitieEntityExtractor.find_entity(ent, text, tokens)
                except ValueError as e:
                    logger.warning("Example skipped: {}".format(str(e)))
                    continue
                sample.add_entity(list(range(start, end)), ent["entity"])
                found_one_entity = True

            trainer.add(sample)
        # Mitie will fail to train if there is not a single entity tagged
        if found_one_entity:
            self.ner = trainer.train()

    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None

        mitie_feature_extractor = kwargs.get("mitie_feature_extractor")
        if not mitie_feature_extractor:
            raise Exception("Failed to train 'intent_featurizer_mitie'. Missing a proper MITIE feature extractor.")

        ents = self.extract_entities(message.text, message.get("tokens"), mitie_feature_extractor)
        extracted = self.add_extractor_name(ents)
        message.set("entities", message.get("entities", []) + extracted, add_to_output=True)

    @classmethod
    def load(cls, model_dir, model_metadata, cached_plugin, **kwargs):
        # type: (Text, Metadata, Optional[MitieEntityExtractor], **Any) -> MitieEntityExtractor
        import mitie

        if model_dir and model_metadata.get("entity_extractor_mitie"):
            entity_extractor_file = os.path.join(model_dir, model_metadata.get("entity_extractor_mitie"))
            extractor = mitie.named_entity_extractor(entity_extractor_file)
            return MitieEntityExtractor(extractor)
        else:
            return MitieEntityExtractor()

    def persist(self, model_dir):
        # type: (Text) -> Dict[Text, Any]

        if self.ner:
            entity_extractor_file = os.path.join(model_dir, "entity_extractor.dat")
            self.ner.save_to_disk(entity_extractor_file, pure_model=True)
            return {"entity_extractor_mitie": "entity_extractor.dat"}
        else:
            return {"entity_extractor_mitie": None}
