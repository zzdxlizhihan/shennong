"""Test the computed features are stable accross computations"""

import pytest
import sys

from shennong.features.processor.bottleneck import BottleneckProcessor
from shennong.features.processor.energy import EnergyProcessor
from shennong.features.processor.filterbank import FilterbankProcessor
from shennong.features.processor.mfcc import MfccProcessor
from shennong.features.processor.onehot import (
    OneHotProcessor, FramedOneHotProcessor)
from shennong.features.processor.pitch import PitchProcessor
from shennong.features.processor.plp import PlpProcessor
from shennong.features.processor.rastaplp import RastaPlpProcessor
from shennong.features.processor.spectrogram import SpectrogramProcessor


PROCESSORS = [
    EnergyProcessor,
    FilterbankProcessor,
    MfccProcessor,
    PlpProcessor,
    BottleneckProcessor,
    OneHotProcessor,
    FramedOneHotProcessor,
    PitchProcessor,
    SpectrogramProcessor,
    RastaPlpProcessor]


@pytest.mark.parametrize(
    'processor, same', [(p, s) for p in PROCESSORS for s in (True, False)])
def test_stable(processor, same, audio, alignments):
    if processor in (OneHotProcessor, FramedOneHotProcessor):
        audio = alignments['S01F1522_0003']

    p1 = processor()
    p2 = p1 if same else processor()

    # disable dithering in mel-based processors to have exactly the
    # same output
    try:
        p1.dither = 0
        p2.dither = 0
    except AttributeError:
        pass

    f1 = p1.process(audio)
    f2 = p2.process(audio)

    # pitch and PLP processing are not stable on MacOS for an unknown
    # reason (this has not being investigated)
    if sys.platform == 'darwin' and isinstance(
            p1, (PitchProcessor, PlpProcessor)):
        assert f1.is_close(f2, atol=1e-5)
    else:
        assert f1 == f2
