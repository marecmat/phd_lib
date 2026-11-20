"""
Minimal tqdm-like progress bar for iterables only
        (used for when you can't install tqdm on your machine)
"""
import shutil
import sys
import time


def _fmt(seconds):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


class tqdm:
    def __init__(self, iterable=None, total=None, desc="", file=None,
                 mininterval=0.1, leave=True, disable=False):
        self.iterable = iterable
        if total is None and iterable is not None:
            try:
                total = len(iterable)
            except TypeError:
                total = None
        self.total = total
        self.desc = desc
        self.file = file or sys.stderr
        self.mininterval = mininterval
        self.leave = leave
        self.disable = disable
        self.n = 0
        self.start = time.time()
        self.last_print = 0.0
        self._refresh(force=True)

    def _line(self):
        elapsed = time.time() - self.start
        rate = self.n / elapsed if elapsed > 0 else 0.0
        prefix = f"{self.desc}: " if self.desc else ""
        if self.total:
            frac = min(self.n / self.total, 1.0)
            eta = (self.total - self.n) / rate if rate > 0 else 0
            stats = (f" {self.n}/{self.total} "
                     f"[{_fmt(elapsed)}<{_fmt(eta)}, {rate:.2f}it/s]")
            head = f"{prefix}{frac * 100:3.0f}%|"
            width = shutil.get_terminal_size((80, 20)).columns
            barlen = max(10, width - len(head) - len(stats) - 1)
            blocks = " ▏▎▍▌▋▊▉█"
            exact = barlen * frac
            full = int(exact)
            partial = blocks[int((exact - full) * 8)] if full < barlen else ""
            bar = ("█" * full + partial).ljust(barlen)
            return f"{head}{bar}|{stats}"
        return f"{prefix}{self.n}it [{_fmt(elapsed)}, {rate:.2f}it/s]"

    def _refresh(self, force=False):
        if self.disable:
            return
        now = time.time()
        if force or now - self.last_print >= self.mininterval:
            self.file.write("\r" + self._line())
            self.file.flush()
            self.last_print = now

    def update(self, n=1):
        self.n += n
        self._refresh()

    def close(self):
        if self.disable:
            return
        self._refresh(force=True)
        self.file.write("\n" if self.leave else "\r\033[K")
        self.file.flush()
        self.disable = True

    def __iter__(self):
        try:
            for obj in self.iterable:
                yield obj
                self.update()
        finally:
            self.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def trange(*args, **kwargs):
    return tqdm(range(*args), **kwargs)

if __name__ == "__main__":
    import time 
    
    for i in tqdm(range(1000)):
        time.sleep(.001)