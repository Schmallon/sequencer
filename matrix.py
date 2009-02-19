from PyQt4 import QtGui, QtCore

class Pitch:
    name_map = {
            'c' : 60,
            'd' : 62,
            'e' : 64,
            'f' : 65,
            'g' : 67,
            'a' : 69,
            'b' : 71,
            }
    def __init__(self, value):
        self.value = value
    def __cmp__(self, other):
        return self.value - other.value
    def is_white(self):
        normalized = self.value % 12
        return normalized in [0, 2, 4, 5, 7, 9, 11]
    def next(self):
        return Pitch(self.value + 1)
    @staticmethod
    def from_name(base, modifier, octave):
        value = Pitch.name_map[str.lower(base)]
        for m in str.lower(modifier):
            if m == '#':
                value = value + 1
            if m == 'b':
                value = value - 1
        value = value + 12 * octave
        return Pitch(value)

def Time(x):
    return x

class Note:
    def __init__(self, pitch, start, duration):
        self.pitch = pitch
        self.start = start
        self.duration = duration
    def end(self):
        return self.start + self.duration

class Matrix:
    def __init__(self):
        self.notes = []
    def add_note(self, note):
        self.notes.append(note)
    def notes_between(self, start, end):
        return [note for note in self.notes if (note.end() > start and
            note.end() < end) or (note.start >= start and
                note.start < end)]


class SeparatorGenerator:
    def __init__(self, offset, duration):
        self.offset = offset
        self.duration = duration
    def get_times_from(self, base):
        current = self.offset
        #TODO: Do this properly
        while current > base:
            current = current - self.duration
        while current < base:
            current = current + self.duration
        while True:
            yield current
            current = current + self.duration

class MatrixEditor(QtGui.QWidget):

    def __init__(self, matrix):
        QtGui.QWidget.__init__(self)
        self.matrix = matrix
        self.lowest_pitch = Pitch.from_name("c", "", 0)
        self.start_time = Time(0)
        self.end_time = Time(5)
        self.width_note_used = 8
        self.width_note_unused = 8
        self.width_separator = 1
        self.color_background = QtGui.QColor(255, 255, 255)
        self.color_horizontal_separator = QtGui.QColor(255, 255, 255)
        self.color_white_rest = QtGui.QColor(212, 212, 212)
        self.color_black_rest = QtGui.QColor(182, 182, 182)
        self.color_note = QtGui.QColor(173, 5, 164)
        self.color_current_grid = QtGui.QColor(255, 255, 255)
        self.color_alternative_grid = QtGui.QColor(171, 171, 171)
        self.separator_alternative = SeparatorGenerator(Time(0), Time(1 / 3.0))
        self.separator_current = SeparatorGenerator(Time(0), Time(1 / 4.0))

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), self.color_note)
        self.paint_rests(painter)
        self.paint_separators(painter, self.separator_alternative,
                self.color_alternative_grid)
        self.paint_horizontal_separators(painter)
        self.paint_separators(painter, self.separator_current,
                self.color_current_grid)
        self.paint_notes(painter)
        painter.end()

    def paint_notes(self, painter):
        for note in self.matrix.notes_between(self.start_time, self.end_time):
            #Ensure no separators are overpainted
            xstart = self.width_separator + self.time_to_xoffset(note.start - self.start_time)
            width = self.time_to_xoffset(note.duration) - self.width_separator
            ypos, height = self.pitch_to_ypos(note.pitch)

            painter.fillRect(xstart, ypos, width, height, self.color_note)

    def paint_rests(self, painter):
        for pitch, ypos, width in self.visible_pitches():
            if pitch.is_white():
                color = self.color_white_rest
            else:
                color = self.color_black_rest
            painter.fillRect(0, ypos, self.width(), width, color)

    def paint_horizontal_separators(self, painter):
        for pitch, ypos, width in self.visible_pitches():
            painter.fillRect(0, ypos + width, self.width(), self.width_separator,
                    self.color_horizontal_separator)

    def paint_separators(self, painter, separator, color):
        for time in separator.get_times_from(self.start_time):
            print time
            if time >= self.end_time:
                break
            xpos = self.time_to_xoffset(time - self.start_time)
            painter.fillRect(xpos, 0, self.width_separator, self.height(),
                    color)

    def time_to_xoffset(self, time):
        relative_position = time / (self.end_time -
                self.start_time)
        return self.width() * relative_position

    def visible_pitches(self):
        ypos = 0
        pitch = self.lowest_pitch
        while ypos < self.height():
            if self.note_with_pitch_visible(pitch):
                width = self.width_note_used
            else:
                width = self.width_note_unused
            yield pitch, ypos, width
            ypos = ypos + width + self.width_separator
            pitch = pitch.next()

    def note_with_pitch_visible(self, pitch):
        return any(map(lambda note: note.pitch == pitch,
            self.matrix.notes_between(self.start_time, self.end_time)))

    def pitch_to_ypos(self, target_pitch):
        for pitch, ypos, width in self.visible_pitches():
            if pitch == target_pitch:
                return ypos, width
