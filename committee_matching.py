#!/usr/bin/env python3

from __future__ import annotations

import pandas as pd
import sys
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional


@dataclass
class Member:
    name: str
    preferred_committee: List[Committee] = field(default_factory=list)
    on_a_string: Optional[Committee] = None
    rejected: List[Committee] = field(default_factory=list)

    def recieve_offer(self, comm: Committee) -> bool:
        if self.on_a_string is None:
            on_a_string = comm
            return True
        elif comm == self._decide_between(
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

        assert False


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
        if self.satisfied():
            return
        for _, member in sorted(
                self.preferred_members.items(), key=lambda x: x[0]):
            if self not in member.rejected:
                if member.recieve_offer(self):
                    self.waiting_on.append(member)

                return

    def be_cut_loose(self, member: Member):
        self.waiting_on.remove(member)


def load_csv(file_name: str) -> \
        Tuple[List[Committee], List[Member]]:
    comms = generate_committees()
    df = pd.read_csv(file_name)
    members = []
    for _, row in df.iterrows():
        member = Member(row.name)
        member.preferred_committee.append(comms[row.first_choice])
        member.preferred_committee.append(comms[row.second_choice])
        member.preferred_committee.append(comms[row.third_choice])
        member.preferred_committee.append(comms[row.fourth_choice])
        member.preferred_committee.append(comms[row.fifth_choice])
        member.preferred_committee.append(comms[row.sixth_choice])
        members.append(member)

        for comm in comms.values():
            if comm.name == 'N/A':
                continue
            comm_preference = row[comm.name]
            if comm_preference is None:
                comm_preference = float('inf')
            elif comm_preference in comm.preferred_members.keys():
                print(comm.name, "repeated the number", comm_preference,
                      file=sys.stderr)
                comm_preference += 0.1 * [
                    int(i)
                    for i in comm.preferred_members.keys()
                ].count(comm_preference)

            if comm_preference in comm.preferred_members.keys():
                raise RuntimeError("Something is very wrong.")

            comm.preferred_members[comm_preference] = member

    return list(comms.values()), members


def generate_committees() -> Dict[str, Committee]:
    committees = [
        Committee('Website', 8),
        Committee('Social', 2),
        Committee('Treasurer', 2),
        Committee('Industrial Relations', 9),
        Committee('Public Relations', 9),
        Committee('Curriculum', 9),
        Committee('N/A', 0)
    ]
    return {c.name: c for c in committees}


def main():
    committees, members = load_csv(sys.argv[1])

    while any(not c.satisfied() for c in committees):
        for committee in committees:
            committee.propose_to_next_member()

    for member in members:
        print(member.name, "is on", member.on_a_string.name)


if __name__ == '__main__':
    main()
