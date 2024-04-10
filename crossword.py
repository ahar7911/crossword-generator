import sys, re, math, time, copy

start = time.perf_counter()
# INPUT
dimensions = sys.argv[1]
height = int(dimensions[:dimensions.index('x')])
width = int(dimensions[dimensions.index('x') + 1:])
size = width * height

numBlocks = int(sys.argv[2])

dictFile = sys.argv[3]
crossword = '-' * size


def insert(board, string, index):
    return board[:index] + string + board[index+len(string):]


def coordsToIndex(coords):
    return int(coords[0]) * width + int(coords[1])


def indexToCoords(index):
    if index < 0:
        index += size
    return int(index / width), int(index % width)


def printBoard(board):
    for startIndex in range(0, height * width, width):
        print(' '.join(board[startIndex: startIndex + width]))
    print()


def placeWord(board, word, index, direction):
    if direction == 'H':
        board = insert(board, word, index)
    else:
        for letter in word:
            board = insert(board, letter, index)
            index += width
    return board


def bestBlockPlacement(board):
    heuristicVal = dict()
    for index in range(int(size/2)):
        if board[index] == '#':
            heuristicVal[index] = -math.inf
            continue
        row, col = indexToCoords(index)
        up = row
        down = height - row - 1
        left = col
        right = width - col - 1
        for topRow in range(row):
            if board[coordsToIndex((topRow, col))] == '#':
                up = row - topRow - 1
        for bottomRow in range(row, height):
            if board[coordsToIndex((bottomRow, col))] == '#':
                down = bottomRow - row - 1
                break
        for leftCol in range(col):
            if board[coordsToIndex((row, leftCol))] == '#':
                left = col - leftCol - 1
        for rightCol in range(col, width):
            if board[coordsToIndex((row, rightCol))] == '#':
                right = rightCol - col - 1
                break
        val = 0
        if left >= 3 and right >= 3:
            val += left+right
        if up >= 3 and down >= 3:
            val += up+down
        heuristicVal[index] = val
    orderedBlocks = list(range(0, int(size/2)))
    orderedBlocks.sort(key=lambda index: (heuristicVal[index], index), reverse=True)
    return orderedBlocks


def placeNBlocks(board):
    if numBlocks == 0:
        return board
    if numBlocks == size:
        return '#' * size

    # CENTER SQUARE CASE
    if numBlocks % 2 == 1 and size % 2 == 1:
        board = insert(board, '#', int(size/2))

    board = fillSquares(board)
    return recurPlacingBlocks(board)


def recurPlacingBlocks(board):
    if board.count('#') == numBlocks:
        return board
    if board.count('#') > numBlocks:
        return None

    orderedBlocks = bestBlockPlacement(board)
    for index in orderedBlocks:
        newBoard = board
        impliedIsTaken = False

        rotatedIndex = size - index - 1
        if newBoard[index] != '-' and newBoard[rotatedIndex] != '#':
            continue

        blocksToAdd = [index, rotatedIndex] + list(impliedBlocks(newBoard, index, set())) + list(impliedBlocks(newBoard, rotatedIndex, set()))
        for blockIndex in blocksToAdd:
            if newBoard[blockIndex] in '-#':
                newBoard = insert(newBoard, '#', blockIndex)
            else:
                 impliedIsTaken = True

        if not isNotConnected(newBoard) and noIllegalBlocks(newBoard) and not impliedIsTaken:
            solution = recurPlacingBlocks(newBoard)
            if solution is not None:
                return solution


def noIllegalBlocks(board):
    for rowStart in range(0, len(board), width):
        row = board[rowStart:rowStart+width]
        if re.search(r'(#(-|\w){1,2}#)|(^(-|\w){1,2}#)|(#(-|\w){1,2}$)', row):
            return False
    for colStart in range(0, width):
        col = board[colStart:size:width]
        if re.search(r'(#(-|\w){1,2}#)|(^(-|\w){1,2}#)|(#(-|\w){1,2}$)', col):
            return False
    return True


def isNotConnected(board):
    if '-' not in board:
        return False
    startIndex = board.index('-')
    board = insert(board, '%', startIndex)
    board = areaFill(board, startIndex)
    return board.count('-') != 0


def areaFill(board, index):
    for move in [-1, 1, -width, width]:
        # incorrect row move
        if not (index % width == 0 and move == -1) and not (index % width == width-1 and move == 1):
            newIndex = index + move
            if 0 <= newIndex < len(board) and board[newIndex] not in '#%':
                board = insert(board, '%', newIndex)
                board = areaFill(board, newIndex)
    return board


def impliedBlocks(board, index, alreadyFound):
    impliedIndices = set()
    row, col = indexToCoords(index)
    if 0 < row < 3:
        for newRow in range(0, row):
            impliedIndex = coordsToIndex((newRow, col))
            if impliedIndex not in alreadyFound:
                impliedIndices.add(impliedIndex)
    if height - 3 <= row < height:
        for newRow in range(row+1, height):
            impliedIndex = coordsToIndex((newRow, col))
            if impliedIndex not in alreadyFound:
                impliedIndices.add(impliedIndex)
    if 0 < col < 3:
        for newCol in range(0, col):
            impliedIndex = coordsToIndex((row, newCol))
            if impliedIndex not in alreadyFound:
                impliedIndices.add(impliedIndex)
    if width - 3 <= col < width:
        for newCol in range(col+1, width):
            impliedIndex = coordsToIndex((row, newCol))
            if impliedIndex not in alreadyFound:
                impliedIndices.add(impliedIndex)

    for addRow in range(-3, 4):
        if abs(addRow) > 1 and 0 <= row + addRow < height:
            index = coordsToIndex((row+addRow, col))
            if board[index] == '#':
                if addRow < 0:
                    indices = [coordsToIndex((row+diff, col)) for diff in range(addRow, 0)]
                    for impliedIndex in indices:
                        if impliedIndex not in alreadyFound:
                            impliedIndices.add(impliedIndex)
                else:
                    indices = [coordsToIndex((row + diff, col)) for diff in range(1, addRow+1)]
                    for impliedIndex in indices:
                        if impliedIndex not in alreadyFound:
                            impliedIndices.add(impliedIndex)

    for addCol in range(-3, 3):
        if abs(addCol) > 1 and 0 <= col + addCol < width:
            index = coordsToIndex((row, col+addCol))
            if board[index] == '#':
                if addCol < 0:
                    indices = [coordsToIndex((row, col + diff)) for diff in range(addCol, 0)]
                    for impliedIndex in indices:
                        if impliedIndex not in alreadyFound:
                            impliedIndices.add(impliedIndex)
                else:
                    indices = [coordsToIndex((row, col+diff)) for diff in range(1, addCol + 1)]
                    for impliedIndex in indices:
                        if impliedIndex not in alreadyFound:
                            impliedIndices.add(impliedIndex)

    additionalImplied = set()
    for imIndex in impliedIndices:
        additionalImplied = impliedBlocks(board, imIndex, alreadyFound | impliedIndices | additionalImplied) | additionalImplied

    return impliedIndices | additionalImplied


def fillSquares(board):
    for rowStart in range(0, len(board), width):
        row = board[rowStart:rowStart+width]
        search = re.search(r'(#(-|\w){1,2}#)|(^(-|\w){1,2}#)|(#(-|\w){1,2}$)', row)
        while search is not None:
            for colIndex in range(search.start(), search.end()):
                index = coordsToIndex([int(rowStart/width), colIndex])
                board = insert(board, '#', index)

            row = board[rowStart:rowStart + width]
            search = re.search(r'(#(-|\w){1,2}#)|(^(-|\w){1,2}#)|(#(-|\w){1,2}$)', row)

    for colStart in range(0, width):
        col = board[colStart:size:width]
        search = re.search(r'(#(-|\w){1,2}#)|(^(-|\w){1,2}#)|(#(-|\w){1,2}$)', col)
        while search is not None:
            for rowIndex in range(search.start(), search.end()):
                index = coordsToIndex([rowIndex, colStart])
                board = insert(board, '#', index)

            col = board[colStart:size:width]
            search = re.search(r'(#(-|\w){1,2}#)|(^(-|\w){1,2}#)|(#(-|\w){1,2}$)', col)

    for index, char in enumerate(board):
        if char == '#':
            rotatedIndex = size - index - 1
            board = insert(board, '#', rotatedIndex)

    while not noIllegalBlocks(board):
        board = fillSquares(board)

    if isNotConnected(board):
        board = fillUnconnectedBlocks(board)

    return board


def replaceAll(string, original, new):
    for index, char in enumerate(string):
        if char == original:
            string = insert(string, new, index)
    return string


def fillUnconnectedBlocks(board):
    while isNotConnected(board):
        newBoard = areaFill(board, board.index('-'))
        if newBoard.count('%') + board.count('#') < numBlocks:
            board = replaceAll(newBoard, '%', '#')
        else:
            newBoard = replaceAll(newBoard, '-', '#')
            for index, char in enumerate(newBoard):
                if char == '#':
                    board = insert(board, '#', index)
    return board


# PART 2
def viableWord(possibleWord, string):
    if possibleWord == string:
        return True
    for index in range(len(possibleWord)):
        if string[index] != '-' and possibleWord[index] != string[index]:
            return False
    return True


def findPossWordsAndLetters(string, originalWordArray):
    possLetters = dict()
    possWords = set()
    for word in originalWordArray:
        if viableWord(word, string):
            possWords.add(word)
            for index, char in enumerate(word):
                if index in possLetters:
                    possLetters[index].add(char)
                else:
                    possLetters[index] = set(char)
    for i in possLetters:
        possLetters[i] = list(possLetters[i])
        possLetters[i].sort(key=lambda char: letterFreq[char], reverse=True)
    return possWords, possLetters


def findBlanksWithPossValues(board):
    wordsFound = set()
    possLetters = dict()
    possWords = dict()
    currentSpaceIndex = 0
    blankSpaces = []
    for rowStart in range(0, len(board), width):
        row = board[rowStart:rowStart+width]
        search = re.search(r'(#(-|\w)+#)|(^(-|\w)+#)|(#(-|\w)+$)|^(-|\w)+$', row)
        while search is not None:
            spaceFound = search.group()
            startIndex = rowStart + search.start()
            if spaceFound[0] == '#':
                startIndex += 1

            spaceFound = spaceFound.strip('#')
            length = len(spaceFound)
            if '-' not in spaceFound:
                wordsFound.add(spaceFound)

            blankSpaces.append((startIndex, length, 'H'))
            possWords[currentSpaceIndex], lettersByStringIndex = findPossWordsAndLetters(spaceFound, wordsByLetterCount[length])

            for index in range(len(spaceFound)):
                actualIndex = startIndex + index
                if actualIndex in possLetters:
                    possLetters[actualIndex] = list(set(possLetters[actualIndex]) & set(lettersByStringIndex[index]))
                else:
                    possLetters[actualIndex] = lettersByStringIndex[index]

                if actualIndex in indexToSpaces:
                    indexToSpaces[actualIndex].append(currentSpaceIndex)
                else:
                    indexToSpaces[actualIndex] = [currentSpaceIndex]

            row = insert(row, '^' * len(spaceFound), search.start())
            search = re.search(r'(#(-|\w)+#)|(^(-|\w)+#)|(#(-|\w)+$)|^(-|\w)+$', row)

            currentSpaceIndex += 1

    for colStart in range(0, width):
        col = board[colStart:size:width]
        search = re.search(r'(#(-|\w)+#)|(^(-|\w)+#)|(#(-|\w)+$)|^(-|\w)+$', col)
        while search is not None:
            spaceFound = search.group()
            startIndex = colStart + search.start() * width
            if spaceFound[0] == '#':
                startIndex += width

            spaceFound = spaceFound.strip('#')
            length = len(spaceFound)
            if '-' not in spaceFound:
                wordsFound.add(spaceFound)

            blankSpaces.append((startIndex, length, 'V'))
            possWords[currentSpaceIndex], lettersByStringIndex = findPossWordsAndLetters(spaceFound, wordsByLetterCount[length])

            for index in range(len(spaceFound)):
                actualIndex = startIndex+index*width
                if actualIndex in possLetters:
                    if index not in lettersByStringIndex:
                        print()
                    possLetters[actualIndex] = list(set(possLetters[actualIndex]) & set(lettersByStringIndex[index]))
                else:
                    possLetters[actualIndex] = lettersByStringIndex[index]

                if actualIndex in indexToSpaces:
                    indexToSpaces[actualIndex].append(currentSpaceIndex)
                else:
                    indexToSpaces[actualIndex] = [currentSpaceIndex]

            col = insert(col, '^' * len(spaceFound), search.start())
            search = re.search(r'(#(-|\w)+#)|(^(-|\w)+#)|(#(-|\w)+$)|^(-|\w)+$', col)

            currentSpaceIndex += 1

    for key in possLetters:
        possLetters[key] = list(set(possLetters[key]))

    return blankSpaces, possLetters, possWords, wordsFound


def mostConstrainedIndex(board, possLetters):
    mostConstrained = (-1, math.inf)
    for index in range(size):
        if board[index] != '#':
            if len(possLetters[index]) == 1 and board[index] == '-':
                board = insert(board, possLetters[index][0], index)
            if 1 < len(possLetters[index]) < mostConstrained[1]:
                mostConstrained = (index, len(possLetters[index]))
    return board, mostConstrained[0]


def updateDeterminedValue(board, index, prevWords, possLetters, possWords):
    newPrevWords = copy.copy(prevWords)
    newPossLetters = copy.copy(possLetters)
    newPossWords = copy.copy(possWords)

    spaceIndices = indexToSpaces[index]
    for spaceIndex in spaceIndices:
        startIndex, length, direction = possibleWordSpaces[spaceIndex]
        if direction == 'H':
            string = board[startIndex:startIndex+length]
        else:
            string = board[startIndex:startIndex+length*width:width]
        if string.count('-') == 0:
            if string in newPrevWords:
                return None
            newPrevWords.add(string)
        newPossWords[spaceIndex], possLettersByStringIndex = findPossWordsAndLetters(string, newPossWords[spaceIndex])
        if len(newPossWords[spaceIndex]) == 0:
            return None

        for index in range(len(string)):
            if direction == 'H':
                boardIndex = startIndex+index
            else:
                boardIndex = startIndex+index*width
            newPossLetters[boardIndex] = possLettersByStringIndex[index]
            if len(possLetters[boardIndex]) == 0:
                return None
            if len(newPossLetters[boardIndex]) == 1 and board[boardIndex] == '-':
                letter = newPossLetters[boardIndex][0]
                board = insert(board, letter, boardIndex)
                result = updateDeterminedValue(board, boardIndex, newPrevWords, newPossLetters, newPossWords)
                if result is None:
                    return None
                board, newPossLetters, newPossWords, newPrevWords = result
    return board, newPossLetters, newPossWords, newPrevWords


def placeWords(board, prevWords, possLetters, possWords):
    if board.count('-') == 0:
        return board
    board, index = mostConstrainedIndex(board, possLetters)
    for letter in possLetters[index]:
        newBoard = insert(board, letter, index)
        result = updateDeterminedValue(newBoard, index, prevWords, possLetters, possWords)
        if result is None:
            continue
        newBoard, newPossLetters, newPossWords, newPrevWords = result
        printBoard(newBoard)

        solution = placeWords(newBoard, newPrevWords, newPossLetters, newPossWords)
        if solution is not None:
            return solution
    return None


# SEED STRINGS
for x in range(4, len(sys.argv)):
    seedString = sys.argv[x]
    coordSearch = re.search(r'\d*x\d*', seedString)
    seedIndex = coordsToIndex(coordSearch.group().split('x'))
    seedWord = seedString[coordSearch.end():]
    crossword = placeWord(crossword, seedWord.upper(), seedIndex, seedString[0].upper())

# PART 1: PLACING BLOCKING SQUARES
crossword = placeNBlocks(crossword)
printBoard(crossword)

# READ IN DICTIONARY
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
letterFreq = {char: 0 for char in alphabet}
wordSet = set()
wordsByLetterCount = dict()

with open(dictFile) as f:
    for line in f:
        dictWord = line.strip().upper()
        if not dictWord.isalpha() or len(dictWord) < 3:
            continue
        for char in dictWord:
            letterFreq[char] = letterFreq[char] + 1
        wordSet.add(dictWord)

        if len(dictWord) in wordsByLetterCount:
            wordsByLetterCount[len(dictWord)].append(dictWord)
        else:
            wordsByLetterCount[len(dictWord)] = [dictWord]


indexToSpaces = dict()
possibleWordSpaces, possLettersPerIndex, possWordsPerSpace, establishedWords = findBlanksWithPossValues(crossword)

for i in range(size):
    if crossword[i] != '#':
        possLettersPerIndex[i].sort(key=lambda char: letterFreq[char], reverse=True)

crossword = placeWords(crossword, establishedWords, possLettersPerIndex, possWordsPerSpace)
end = time.perf_counter()
print(end-start)

printBoard(crossword)