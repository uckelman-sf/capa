import logging
import itertools
import collections
from typing import Any, Tuple

from capa.rules import Scope, RuleSet
from capa.engine import FeatureSet, MatchResults
from capa.features.address import NO_ADDRESS
from capa.features.extractors.base_extractor import FeatureExtractor, StaticFeatureExtractor, DynamicFeatureExtractor

logger = logging.getLogger("capa")


def find_file_capabilities(ruleset: RuleSet, extractor: FeatureExtractor, function_features: FeatureSet):
    file_features: FeatureSet = collections.defaultdict(set)

    for feature, va in itertools.chain(extractor.extract_file_features(), extractor.extract_global_features()):
        # not all file features may have virtual addresses.
        # if not, then at least ensure the feature shows up in the index.
        # the set of addresses will still be empty.
        if va:
            file_features[feature].add(va)
        else:
            if feature not in file_features:
                file_features[feature] = set()

    logger.debug("analyzed file and extracted %d features", len(file_features))

    file_features.update(function_features)

    _, matches = ruleset.match(Scope.FILE, file_features, NO_ADDRESS)
    return matches, len(file_features)


def find_capabilities(
    ruleset: RuleSet, extractor: FeatureExtractor, disable_progress=None, **kwargs
) -> Tuple[MatchResults, Any]:
    from capa.features.capabilities.static import find_static_capabilities
    from capa.features.capabilities.dynamic import find_dynamic_capabilities

    if isinstance(extractor, StaticFeatureExtractor):
        # for the time being, extractors are either static or dynamic.
        # Remove this assertion once that has changed
        assert not isinstance(extractor, DynamicFeatureExtractor)
        return find_static_capabilities(ruleset, extractor, disable_progress=disable_progress, **kwargs)
    if isinstance(extractor, DynamicFeatureExtractor):
        return find_dynamic_capabilities(ruleset, extractor, disable_progress=disable_progress, **kwargs)
    else:
        raise ValueError(f"unexpected extractor type: {extractor.__class__.__name__}")
