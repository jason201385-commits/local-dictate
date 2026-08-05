# -*- coding: utf-8 -*-
"""PyInstaller runtime hook:用 stub 取代 av(PyAV / FFmpeg)。

**為什麼不打包 FFmpeg**(2026-07-30 查證,有實際證據):

PyAV 的 Windows 官方 wheel 內含 `libx264` 與 `libx265`——兩者都是 **GPL-2.0-or-later**。
從 avcodec DLL 抽出的 FFmpeg 內嵌組態字串是:

    --enable-version3 --enable-libx264 --enable-libx265

把這批 DLL 跟本程式放進同一個安裝檔散布,義務就不只是「附上授權原文」,
而是整包要依 GPL 條款散布並提供完整對應原始碼。

而 local-dictate **執行期根本用不到它們**:麥克風錄到的音訊在 dictate.py 裡
是 `np.frombuffer(...).astype(np.float32)` 直接餵給 `model.transcribe()`,
從來不走 faster-whisper 的檔案解碼路徑。av 只有 `faster_whisper/audio.py`
的 `decode_audio()` 會用到,而那是「從音檔轉錄」才需要的。

所以最乾淨的處理是**不要散布它**:產物少約 25MB,GPL 問題不存在,功能零損失。

代價:打包版不能從音檔轉錄(`decode_audio`)。走到那條路時會拿到下面這段
說明,而不是一個看不懂的 AttributeError。要用音檔轉錄請從原始碼執行。
"""
import sys
import types

_MSG = (
    "這個版本沒有打包 FFmpeg(av)。\n"
    "原因:PyAV 的 Windows wheel 內含 libx264/libx265(GPL-2.0+),"
    "而 local-dictate 的即時聽寫完全用不到——麥克風音訊是 numpy array 直接進模型。\n"
    "只有『從音檔轉錄』需要 FFmpeg,請改從原始碼執行(pip install av)。"
)


class _AVStub(types.ModuleType):
    """能被 import,但真的去碰它的時候給出人看得懂的理由。"""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        raise RuntimeError(_MSG)


if "av" not in sys.modules:
    _stub = _AVStub("av")
    _stub.__version__ = "stub (FFmpeg 未打包,見 THIRD_PARTY_NOTICES.md)"
    sys.modules["av"] = _stub
