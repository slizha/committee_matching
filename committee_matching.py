#!/usr/bin/env python3

from __future__ import annotations

import pandas as pd
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Union


@dataclass
class Member:
    name: str
    preferred_committee: List[Committee] = field(default_factory=list)
    on_a_string: Committee = None
    rejected: List[Committee] = field(default_factory=list)

    def recieve_offer(self, comm):
        if self.on_a_string is None:
            on_a_string = comm
            return True
        elif comm == self.preferred_committee.decide_between(
                on_a_string, comm):
            on_a_string.be_cut_loose(self)
            self.rejected.append(on_a_string)
            on_a_string = comm
            return True
        else:
            self.rejected.append(comm)
            return False

    def _decide_between(self, opt_1: Committee, opt_2: Committee) -> Committee:
        for opt in self.preferred_committee:
            if opt == opt_1:
                return opt_1
            elif opt == opt_2:
                return opt_2


@dataclass
class Committee:
    name: str
    open_spots: int
    preferred_members: Dict[float, Member] = \
        field(default_factory=dict)
    waiting_on: List[Member] = field(default_factory=list)

    def satisfied(self) -> bool:
        return self.open_spots == len(self.waiting_on)

    def propose_to_next_member(self):
        for _, member in sorted(
                self.preferred_members.items(), key=lambda x: x[0]):
            if self not in member.rejected:
                if member.recieve_offer(self):
                    self.waiting_on.append(member)

    def be_cut_loose(self, member: Member):
        self.waiting_on.remove(member)


def load_csv(file_name: str) -> \
        Tuple[List[Committee], List[Member]]:
    df = pd.read_csv(file_name)


def generate_committees() -> Dict[str, Committee]:
    committees = [
        Committee('Website', 8),
        Committee('Social', 2),
        Committee('Treasurer', 2),
        Committee('Industrial Relations', 9),
        Committee('Public Relations', 9),
        Committee('Curriculum', 9),
    ]
    return {c.name: c for c in committees}
