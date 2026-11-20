import os

def save_to_logs(fig, name, **kwargs):
    path = os.environ["FIG_PATH"]
    fig.savefig(path+name, **kwargs)