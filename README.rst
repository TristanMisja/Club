Club
====
| **Club** is a simple, yet powerful, library to simplify making command-line programs.
| 
| It has functions and classes such as ``fancyprint()``, ``DevNull``, and ``Stack``.
|
| ``>>> import club``
| ``>>> club.fancyprint("Hello, I'm", 69, "years old", sep=" ", case="leetcase")``
| ``"H3ll0, 1'm 69 y34r5 0ld"``
| ``>>> stack = club.Stack()``
| ``>>> stack.push("plum")``
| ``>>> stack.push("cherry")``
| ``>>> print(stack.pop())``
| ``"cherry"``
|

Installation
============
| Club can be installed using pip:
| 
| ``$ python3 -m pip install club``
| 
| Club so far only supports Python 3.