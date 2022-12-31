from dataclasses import dataclass

from query.query import Query
from update import Update
from config import Config
from parse.parse import Parse 

@dataclass
class Bot:
    config: Config
    query: Query
    update: Update
    parse: Parse