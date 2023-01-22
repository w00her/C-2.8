import random


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Это был выстрел за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Эта клетка уже использована!"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, *decks, direction):
        self.lengh = decks
        self.bow_position = self.lengh[0]
        self.direction = direction
        self.lifes = len(decks)

    @property
    def dots(self):
        ship_dots = []
        for i in self.lengh:
            ship_dots.append(Dot(i[0], i[1]))
        return ship_dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.field = [["O"]*self.size for _ in range(self.size)]
        self.ships = []
        self.hid = hid
        self.busy = []
        self.count = 0

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, drowned=False):
        safety_contour = [
            (-1, 1), (0, 1), (1, 1),
            (-1, 0), (1, 0),
            (-1, -1), (0, -1), (1, -1)
        ]
        for ship_dot in ship.dots:
            for cntr, cntr_y in safety_contour:
                cntr = Dot(ship_dot.x + cntr, ship_dot.y + cntr_y)
                if not (self.out(cntr)) and cntr not in self.busy:
                    if drowned:
                        self.field[cntr.x][cntr.y] = "."
                    self.busy.append(cntr)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, bullet):
        return not ((0 <= bullet.x < self.size) and (0 <= bullet.y < self.size))

    def shot(self, bullet):
        if self.out(bullet):
            raise BoardOutException()

        if bullet in self.busy:
            raise BoardUsedException()

        self.busy.append(bullet)

        for ship in self.ships:
            if bullet in ship.dots:
                ship.lives -= 1
                self.field[bullet.x][bullet.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, drowned=True)
                    print("Корабль потоплен!")
                    return False
                print("Корабль подбит!")
                return True

        self.field[bullet.x][bullet.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, my_board, enemy_board):
        self.board = my_board
        self.enemy = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                ask_shot = self.ask()
                answer_damage = self.enemy.shot(ask_shot)
                return answer_damage
            except BoardException as error:
                print(error)


class AI(Player):
    def ask(self):
        dot = Dot(random.randint(1, 6), random.randint(1, 6))
        print(f"Ход компьютера: {dot.x} {dot.y}")
        return dot


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.size = size
        human = self.random_board()
        pc = self.random_board()
        pc.hid = True

        self.ai = AI(pc, human)
        self.us = User(human, pc)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        fleet = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for vessel_decks in fleet:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                direction = random.choice(('vertical', 'horizontal'))
                bow_position = [
                    Dot(random.randint(1, 6), random.randint(1, 6))]
                if vessel_decks > 1:
                    if direction == 'vertical':
                        for i in range(1, vessel_decks + 1):
                            bow_position.append(
                                Dot(bow_position[0].x + i, bow_position[0].y))
                    if direction == 'horizontal':
                        for i in range(1, vessel_decks + 1):
                            bow_position.append(
                                Dot(bow_position[0].x, bow_position[0].y+i))
                ship = Ship(bow_position, direction=direction)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("    Морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
