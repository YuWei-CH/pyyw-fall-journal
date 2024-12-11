import data.db_connect as dbc


TITLE = 'title'
AUTHOR = 'author'
REFEREES = 'referees'

MANUSCRIPTS_COLLECT = 'manuscripts'


def read():
    manuscripts = dbc.read_dict(MANUSCRIPTS_COLLECT, TITLE)
    return manuscripts


def read_one(title: str) -> dict:
    return dbc.read_one(MANUSCRIPTS_COLLECT, {TITLE: title})


def exists(title: str) -> bool:
    return read_one(title) is not None


def create(title: str, author: str):
    manuscript = {
        TITLE: title,
        AUTHOR: author,
        REFEREES: [],
    }
    dbc.create(MANUSCRIPTS_COLLECT, manuscript)
    return title


# Add referees

# Delete referees

def delete(title: str):
    del_num = dbc.delete(MANUSCRIPTS_COLLECT, {TITLE: title})
    return title if del_num == 1 else None


def update(title: str, author: str, referees: str):
    if not exists(title):
        raise ValueError(f'Updating non-existent manuscript: {title=}')
    if not author.strip():
        raise ValueError("Author can't be blank. ")
    dbc.update(MANUSCRIPTS_COLLECT, {TITLE: title},
               {AUTHOR: author, REFEREES: referees})
    return title
