#!/usr/bin/env python
# coding:utf-8


class A(object):
    def __init__(self):
        self.l = [[1,2,3],[4,5,3],[2,1]]
        self.n = 3

    def d(self):
        for i in range(len(self.l)-1, -1, -1):
            if self.n in self.l[i]:
                print("remove: ", self.l[i])
                self.l.remove(self.l[i])

    def print(self):
        print(self.l)


def main():
    a = A()
    a.print()
    a.d()
    a.print()


if __name__ == '__main__':
    main()
