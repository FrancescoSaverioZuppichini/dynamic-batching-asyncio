from typing import ClassVar as _ClassVar
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class InferenceReply(_message.Message):
    __slots__ = ["batch_id", "pred"]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    PRED_FIELD_NUMBER: _ClassVar[int]
    batch_id: int
    pred: int
    def __init__(
        self, batch_id: _Optional[int] = ..., pred: _Optional[int] = ...
    ) -> None: ...

class InferenceRequest(_message.Message):
    __slots__ = ["data"]

    class InferenceData(_message.Message):
        __slots__ = ["image"]
        IMAGE_FIELD_NUMBER: _ClassVar[int]
        image: str
        def __init__(self, image: _Optional[str] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: InferenceRequest.InferenceData
    def __init__(
        self, data: _Optional[_Union[InferenceRequest.InferenceData, _Mapping]] = ...
    ) -> None: ...
