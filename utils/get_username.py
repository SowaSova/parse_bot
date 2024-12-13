from config.constants import TG_URL


def get_username(link: str) -> str:
    if link.startswith("@"):
        return link[1:]
    elif link.startswith(TG_URL):
        return link[len(TG_URL) :]
    else:
        return link
