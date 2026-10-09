import numpy as np
import time
import sys
from typing import List, Dict, Any

class TimeTravelReplayEngine:
    def __init__(self, sample_rate: int = 20480):
        self.sample_rate = sample_rate
        self.buffer: List[Dict[str, Any]] = []
        self.current_index: int = 0
        self.bookmarks: Dict[str, int] = {}

    def ingest_frame(self, timestamp: float, raw_signal: np.ndarray, metadata: Dict[str, Any] = None):
        """Buffer high-frequency signal frame into timeline."""
        frame = {
            "index": len(self.buffer),
            "timestamp": timestamp,
            "signal": raw_signal,
            "rms": float(np.sqrt(np.mean(raw_signal ** 2))),
            "peak": float(np.max(np.abs(raw_signal))),
            "metadata": metadata or {}
        }
        self.buffer.append(frame)

    def add_bookmark(self, tag: str, index: int = None):
        """Bookmark a critical timestamp/index (e.g. MicroCrack_Initiation, BPFO_Spike)."""
        idx = index if index is not None else self.current_index
        if 0 <= idx < len(self.buffer):
            self.bookmarks[tag] = idx

    def seek_to_index(self, index: int) -> Dict[str, Any]:
        """Seek directly to a specific time index."""
        if not self.buffer:
            raise ValueError("Buffer is empty!")
        self.current_index = max(0, min(index, len(self.buffer) - 1))
        return self.buffer[self.current_index]

    def seek_to_bookmark(self, tag: str) -> Dict[str, Any]:
        """Jump timeline directly to a named bookmark."""
        if tag not in self.bookmarks:
            raise KeyError(f"Bookmark '{tag}' not found.")
        return self.seek_to_index(self.bookmarks[tag])

    def replay_sequence(self, start_idx: int, end_idx: int, speed_factor: float = 1.0) -> List[Dict[str, Any]]:
        """Replay frames from start to end with speed adjustment."""
        sequence = []
        start_idx = max(0, start_idx)
        end_idx = min(len(self.buffer) - 1, end_idx)
        for idx in range(start_idx, end_idx + 1):
            frame = self.seek_to_index(idx)
            sequence.append(frame)
        return sequence

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=== Stage 61: Time-Travel Replay Engine Test ===")
    engine = TimeTravelReplayEngine(sample_rate=20480)
    
    # Ingest 100 synthetic 1-ms frames
    t_start = 1700000000.0
    for i in range(100):
        t = t_start + i * 0.001
        sig = np.random.normal(0, 0.1 + (i/100.0)**2, 1024)
        engine.ingest_frame(timestamp=t, raw_signal=sig, metadata={"stage": "degradation" if i > 70 else "normal"})
        if i == 75:
            engine.add_bookmark("MicroCrack_Spike", i)

    print(f"Total Buffered Frames: {len(engine.buffer)}")
    bm_frame = engine.seek_to_bookmark("MicroCrack_Spike")
    print(f"Bookmarked Frame [MicroCrack_Spike]: Index={bm_frame['index']}, Timestamp={bm_frame['timestamp']:.3f}, RMS={bm_frame['rms']:.4f}")
    
    seq = engine.replay_sequence(70, 80)
    print(f"Replayed sequence from frame 70 to 80 ({len(seq)} frames).")
    print("Stage 61 execution complete.")
