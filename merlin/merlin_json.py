import enum
import json
import logging
from collections import OrderedDict, deque

import numpy as np
from maestrowf.abstracts import enums as maestro_enums
from maestrowf.datastructures.core.executiongraph import ExecutionGraph, _StepRecord
from maestrowf.datastructures.core.study import StudyStep
from maestrowf.datastructures.environment import Variable

from merlin.common.sample_index import SampleIndex
from merlin.study.dag import MerlinDAG
from merlin.study.step import MerlinStep


MAESTRO_ENUMS = {
    "State": maestro_enums.State,
    "JobStatusCode": maestro_enums.JobStatusCode,
    "SubmissionCode": maestro_enums.SubmissionCode,
    "CancelCode": maestro_enums.CancelCode,
    "StudyStatus": maestro_enums.StudyStatus,
}


LOG = logging.getLogger(__name__)


class MerlinEncoder(json.JSONEncoder):
    """
    Encode Merlin / Maestro objects into a json string.
    """

    @staticmethod
    def to_dict(obj, lvl=0):
        """
        Makes a Merlin or Maestro object into nested python objects recognized by
        json, such as dict, str, list, int, etc.
        """
        print(lvl * "  " + str(type(obj)))
        if type(obj) == tuple or "celery" in str(type(obj)):
            print(lvl * "  " + str(obj))
        if "celery" in str(type(obj)):
            print(lvl * "  " + str(obj.__dict__))
        if obj is None:
            return {"__None__": ""}
        if type(obj) in {str, int, float, bool}:
            return obj
        if type(obj) == list:
            result = []
            for item in obj:
                result.append(MerlinEncoder.to_dict(item, lvl + 1))
            return {"__list__": result}
        if type(obj) == tuple:
            result = []
            for item in obj:
                result.append(MerlinEncoder.to_dict(item, lvl + 1))
            return {"__tuple__": tuple(result)}
        if type(obj) == dict:
            result = {}
            for k, v in obj.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return result
        if isinstance(obj, enum.Enum):
            return {"__enum__": str(obj)}
        if isinstance(obj, np.ndarray):
            return {"__ndarray__": obj.tolist()}
        if isinstance(obj, Variable):
            result = {}
            for k, v in obj.__dict__.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return {"__Variable__": result}
        if isinstance(obj, StudyStep):
            result = {}
            for k, v in obj.__dict__.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return {"__StudyStep__": result}
        if isinstance(obj, set):
            result = []
            for item in obj:
                result.append(MerlinEncoder.to_dict(item, lvl + 1))
            return {"__set__": result}
        if isinstance(obj, deque):
            result = []
            for item in obj:
                result.append(MerlinEncoder.to_dict(item, lvl + 1))
            return {"__deque__": result}
        if isinstance(obj, OrderedDict):
            result = {}
            for k, v in obj.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return {"__OrderedDict__": result}
        if isinstance(obj, _StepRecord):
            result = {}
            for k, v in obj.__dict__.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return {"___StepRecord__": result}
        if isinstance(obj, ExecutionGraph):
            result = {}
            for k, v in obj.__dict__.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return {"__ExecutionGraph__": result}
        if isinstance(obj, MerlinDAG):
            result = {}
            for k, v in obj.__dict__.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return {"__MerlinDAG__": result}
        if isinstance(obj, MerlinStep):
            result = {}
            for k, v in obj.__dict__.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return {"__MerlinStep__": result}
        if isinstance(obj, SampleIndex):
            result = {}
            for k, v in obj.__dict__.items():
                result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            return {"__SampleIndex__": result}
        else:
            #print(f"Trying to serialize type '{type(obj)}' with catch-all hack...")
            #result = {}
            #for k, v in obj.__dict__.items():
            #    result[k] = MerlinEncoder.to_dict(v, lvl + 1)
            #return {f"__{str(type(obj))}__": result}
            try:
                print(
                    f"Trying to serialize type '{type(obj)}' (not supported by MerlinEncoder) with regular json..."
                )
                return json.loads(json.dumps(obj))
            except TypeError as e:
                import pickle

                pickle.dump(obj, open("OFFENDING_OBJ.pickle", "wb"))
                raise TypeError(
                    f"Type '{type(obj)}' not supported by MerlinEncoder or regular json! Json exception: {e}"
                )

    def encode(self, obj):
        try:
            return json.dumps(obj)
        except TypeError as e:
            dct = MerlinEncoder.to_dict(obj)
            return json.dumps(dct)
        except Exception as e:
            print(f"Broke on object of type {type(obj)}: {obj}")
            raise e2


class MerlinDecoder(json.JSONDecoder):
    """
    Decode Merlin / Maestro objects from json.
    """

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_obj)

    def dict_to_obj(self, dct):
        if "__None__" in dct:
            return None
        if "__enum__" in dct:
            name, member = dct["__enum__"].split(".")
            return getattr(MAESTRO_ENUMS[name], member)
        if "__ndarray__" in dct:
            return np.asarray(dct["__ndarray__"])
        if "__list__" in dct:
            return list(dct["__list__"])
        if "__tuple__" in dct:
            return tuple(dct["__tuple__"])
        if "__set__" in dct:
            return set(dct["__set__"])
        if "__deque__" in dct:
            return deque(dct["__deque__"])
        if "__OrderedDict__" in dct:
            return OrderedDict(dct["__OrderedDict__"])
        if "__Variable__" in dct:
            return Variable(**dct["__Variable__"])
        if "__StudyStep__" in dct:
            dct = dct["__StudyStep__"]
            result = StudyStep()
            for k, v in dct.items():
                setattr(result, k, v)
            result.name = dct["name"]
            result.description = dct["description"]
            result.run = dct["run"]
            return result
        if "___StepRecord__" in dct:
            dct = dct["___StepRecord__"]
            dummy_step = StudyStep()
            result = _StepRecord("workspace", dummy_step)
            for k, v in dct.items():
                setattr(result, k, v)
            return result
        if "__ExecutionGraph__" in dct:
            dct = dct["__ExecutionGraph__"]
            result = ExecutionGraph()
            for k, v in dct.items():
                setattr(result, k, v)
            return result
        if "__MerlinStep__" in dct:
            dct = dct["__MerlinStep__"]
            dummy_step = StudyStep()
            dummy_step_record = _StepRecord("workspace", dummy_step)
            result = MerlinStep(dummy_step_record)
            for k, v in dct.items():
                setattr(result, k, v)
            return result
        if "__MerlinDAG__" in dct:
            dct = dct["__MerlinDAG__"]
            result = MerlinDAG(ExecutionGraph(), None)
            for k, v in dct.items():
                setattr(result, k, v)
            return result
        if "__SampleIndex__" in dct:
            dct = dct["__SampleIndex__"]
            result = SampleIndex(1, 10, {}, "")
            for k, v in dct.items():
                setattr(result, k, v)
            return result
        else:
            return dct


def encode(obj):
    encoder = MerlinEncoder()
    return encoder.encode(obj)


def decode(json_str):
    decoder = MerlinDecoder()
    return decoder.decode(json_str)
