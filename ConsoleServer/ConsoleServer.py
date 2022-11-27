
import curses, socket

# define set of keys that can be used
KEY_REGULAR=range(32,127)
KEY_RIGHT=curses.KEY_RIGHT
KEY_LEFT=curses.KEY_LEFT
KEY_UP=curses.KEY_UP
KEY_DOWN=curses.KEY_DOWN
KEY_ENTER=10
KEY_BACKSPACE=263
KEY_ESCAPE=27

class Buffer():
    '''
    Data, cursor position and scroll window
    '''
    def __init__(self, max_row, max_col):
        self._buffer=[[]] # holds data to be printed
        self._max_row=max_row
        self._max_col=max_col
        self._current_row=0
        self._current_col=0
        self._row_offset=0
        self._col_offset=0
    
    def _update_scroll_window(self):
        # Update the scrolling window location
        if self._current_row < self._row_offset: # if current low is less then we are scrolling up
            self._row_offset = self._current_row 
        if self._current_row >= self._row_offset + self._max_row:# if current row exceeds the scrolling window max rows then we are scrolling down
            self._row_offset = self._current_row - self._max_row + 1 
        if self._current_col < self._col_offset:  # we are scrolling left
            self._col_offset = self._current_col
        if self._current_col >= self._col_offset + self._max_col:  # we are scrolling right
            self._col_offset = self._current_col - self._max_col + 1
    
    @property
    def current_row(self):
        return self._current_row-self._row_offset
    
    @property
    def current_col(self):
        return self._current_col-self._col_offset

    def get_data(self):
        '''
        Retrieve all the data in current scrolling window
        '''
        self._update_scroll_window()
        for row in range(self._max_row): 
            buf_row = row + self._row_offset
            if buf_row >= len(self._buffer):
                break
            for col in range(self._max_col): 
                buf_col = col + self._col_offset 
                if buf_col >= len(self._buffer[buf_row]):
                    yield row, col, "\n"
                    break
                else:
                    yield row, col, self._buffer[buf_row][buf_col]
    
    def add(self, key):
        '''
        Add key into buffer in current cursor position
        '''
        self._buffer[self._current_row].insert(self._current_col, key)
        self._current_col+=1
    
    def newline(self):
        '''
        Enter new line on current cursor position row
        '''
        line=self._buffer[self._current_row][self._current_col:] # if in the middle of a row, then split the line
        self._buffer[self._current_row]=self._buffer[self._current_row][:self._current_col]
        self._current_row+=1 # move line down
        self._current_col=0 # and in the beginning of the line
        self._buffer.insert(self._current_row, []+line) # insert the other half of split line
        
    def delete(self):
        '''
        Delete a character on current cursor position
        '''
        if self._current_col != 0:  
            self._current_col-=1 
            del self._buffer[self._current_row][self._current_col] # remove that character from the characters buffer
        elif self._current_row != 0: 
            line = self._buffer[self._current_row][self._current_col:] # save whatever might be on the right of the cursor position
            del self._buffer[self._current_row] # remove current row from the characters buffer
            self._current_row-=1 
            self._current_col = len(self._buffer[self._current_row]) # jump to the of the row above this row
            self._buffer[self._current_row] += line # append all the row content from the line below which was to the right of the cursor
    
    def move_right(self):
        '''
        Move cursor one column right
        '''
        if self._current_col < len(self._buffer[self._current_row]):  # if we are not at the end of this row (columns)
            self._current_col+=1
        elif self._current_row < len(self._buffer)-1:  # if we are not in the end of all rows in buffer
            self._current_row+=1
            self._current_col = 0
    
    def move_left(self):
        '''
        Move cursor one column left
        '''
        if self._current_col != 0: # if current column is not 0
            self._current_col -= 1
        elif self._current_row > 0: # if current row is not 0
            self._current_row -= 1
            self._current_col = len(self._buffer[self._current_row]) # jump to the end column of the row above
    
    def move_up(self):
        '''
        Move cursor one row up
        '''
        if self._current_row != 0:
            self._current_row-=1 # just move cursor up
            if len(self._buffer[self._current_row])-1 < self._current_col:
                self._current_col=len(self._buffer[self._current_row])
    
    def move_down(self):
        '''
        Move cursor one row down
        '''
        if self._current_row < len(self._buffer)-1:
            self._current_row += 1
            if len(self._buffer[self._current_row])-1 < self._current_col:
                self._current_col=len(self._buffer[self._current_row])


class Editor(object):
    '''
    classdocs
    ''' 
    def __init__(self, ip, port):
        self.ip=ip
        self.port=port

    def _init_curses(self): 
        # initialize curses library
        self._screen=curses.initscr()
        self._screen.keypad(1) # enable reading function keys
        curses.noecho() # input not printed
        curses.raw() # direct input without host system pre-processing
        max_row, max_col=self._screen.getmaxyx()
        self._buffer=Buffer(max_row, max_col)
    
    def _run(self, _):
        self._init_curses()
        ret=True
        while ret:
            self._render()
            ret=self._handle_input()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.ip, self.port))
            sock.listen()
            try:
                print("Waiting for client connection, press CTRL-C to abort")
                self.conn, _ = sock.accept()
                with self.conn:
                    curses.wrapper(self._run)
            except:
                pass # user aborted

    def _render(self):
        self._screen.erase() # clear old data from screen
        for row, col, char in self._buffer.get_data(): # render new data from buffer
            try:
                self._screen.addch(row, col, char)
            except: # try-except to simplify handling edge cases; we use only basic features of ncurses
                pass
        
        self._screen.move(self._buffer.current_row, self._buffer.current_col) # move the cursor 
        self._screen.refresh() # update the screen with new data
        
    def _handle_input(self):
        key=self._screen.getch() # get key
        self.send(key) # send character to client app
        
        if key in KEY_REGULAR:
            self._buffer.add(key)
        elif key == KEY_ENTER:
            self._buffer.newline()
        elif key == KEY_BACKSPACE:
            self._buffer.delete()
        elif key == KEY_RIGHT:
            self._buffer.move_right()
        elif key == KEY_LEFT:
            self._buffer.move_left()
        elif key == KEY_DOWN:
            self._buffer.move_down()
        elif key == KEY_UP:
            self._buffer.move_up()
        elif key == KEY_ESCAPE:
            return False
        
        return True
    
    def send(self, key):
        key_bytes=key.to_bytes(4, "little")
        self.conn.sendall(key_bytes)
        
if __name__ == '__main__':
    editor=Editor("172.17.0.2", 5000)
    editor.run()