using System;
using System.Net;
using System.Net.Sockets;
using Mindmagma.Curses;
using System.Collections.Generic;

namespace client
{
    class Editor
    {
        static void Main(string[] args)
        {
            // ncurses init stuff
            IntPtr screen = NCurses.InitScreen();
            NCurses.NoEcho(); // disable echoing characters to terminal
            int row_offset = 0, col_offset = 0, current_row = 0, current_col = 0;
            int max_row, max_col;
            NCurses.GetMaxYX(screen, out max_row, out max_col); // get size of the terminal
            int buf_row, buf_col;
            List<List<char>> term_buffer = new List<List<char>>(); // each element will be a row which contains columns for character
            List<char> sub_list = new List<char>();

            // networking init stuff
            Socket sck = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPEndPoint end_point = new IPEndPoint(IPAddress.Parse("172.17.0.2"), 5000);
            sck.Connect(end_point);
            byte[] recv_buffer = new byte[4];
            int recv_bytes_num;

            try
            {
                bool exit = false;
                while (!exit)
                {
                    // implement buffer scrolling
                    if (current_row < row_offset) { row_offset = current_row; } // scrolling up
                    if (current_row >= row_offset + max_row) { row_offset = current_row - max_row + 1; } // scroling down
                    if (current_col < col_offset) { col_offset = current_col; } // scrolling left
                    if (current_col >= col_offset + max_col) { col_offset = current_col - max_col + 1; } // scrolling right

                    // implement rendering
                    NCurses.Move(0, 0); // render from top-left corner

                    for (int row = 0; row < max_row; row++)
                    {
                        buf_row = row + row_offset;
                        if (buf_row >= term_buffer.Count) { break; }
                        for (int col = 0; col < max_col; col++)
                        {
                            buf_col = col + col_offset;
                            try
                            {
                                if (buf_col >= term_buffer[buf_row].Count)
                                {
                                    NCurses.MoveAddChar(row, col, '\n'); // end line with new-line
                                    NCurses.ClearToEndOfLine(); // clear caracters from previous render 
                                    break;
                                }
                                NCurses.MoveAddChar(row, col, term_buffer[buf_row][buf_col]);
                            }
                            catch // catches edge-case of writing on last column of last row - ncurses will throw an error because scrollok is disabled
                            {
                                break;
                            } 
                        }
                    }

                    NCurses.Move(current_row-row_offset, current_col-col_offset);
                    NCurses.Refresh();
                    
                    // receive a character from server
                    recv_bytes_num = sck.Receive(recv_buffer, 0, recv_buffer.Length, 0); 
                    Array.Resize(ref recv_buffer, recv_bytes_num);
                    int recv_char = BitConverter.ToInt32(recv_buffer);

                    // decode character and perform actions accordingly
                    switch (recv_char)
                    {
                        case int n when (n < 128 && n > 31): // regular character in ASCII
                            if (term_buffer.Count <= current_row) // if no characters on this row yet
                            {
                                term_buffer.Add(new List<char>()); // create new list to put characters in
                            }
                            term_buffer[current_row].Insert(current_col, Convert.ToChar(recv_char));
                            current_col++;
                            break;

                        case 10: // ENTER key
                            sub_list = term_buffer[current_row].GetRange(current_col, term_buffer[current_row].Count - current_col); // split line at specified column
                            term_buffer[current_row].RemoveRange(current_col, term_buffer[current_row].Count - current_col); // remove the characters right of specified column
                            current_row++;
                            term_buffer.Insert(current_row, sub_list); // insert the characters into newly created line
                            current_col = 0;
                            break;
                        
                        case CursesKey.BACKSPACE:
                            if (current_col != 0) // if not already at the start of line
                            {
                                current_col--;
                                term_buffer[current_row].RemoveAt(current_col); // remove character
                            }
                            else if (current_row != 0) // we are not at the first line
                            {
                                sub_list = term_buffer[current_row]; // take everything from right side of cursor
                                term_buffer.RemoveAt(current_row); // remove that line
                                current_row--;
                                current_col = term_buffer[current_row].Count; // get the column on new row
                                term_buffer[current_row].AddRange(sub_list); // drop the text from deleted row
                            }
                            break;

                        case CursesKey.LEFT:
                            if (current_col != 0)
                            {
                                current_col--;
                            }
                            else if (current_row > 0)
                            {
                                current_row--;
                                current_col = term_buffer[current_row].Count;
                            }
                            break;

                        case CursesKey.RIGHT:
                            if (current_col < term_buffer[current_row].Count)
                            {
                                current_col++;
                            }
                            else if (current_row < term_buffer.Count-1)
                            {
                                current_row++;
                                current_col = 0;
                            }
                            break;

                        case CursesKey.UP:
                            if (current_row != 0)
                            {
                                current_row--;
                                if (term_buffer[current_row].Count-1 < current_col) // if new row has less columns then jump to row end
                                {
                                    current_col = term_buffer[current_row].Count;
                                }
                            }
                            break;

                        case CursesKey.DOWN:
                            if (current_row < term_buffer.Count-1)
                            {
                                current_row++;
                                if (term_buffer[current_row].Count - 1 < current_col) // if new row has less columns then jump to row end
                                {
                                    current_col = term_buffer[current_row].Count;
                                }
                            }
                            break;

                        case CursesKey.ESC:  // check if server app is closed
                            exit = true;
                            break;

                        default: // if any other KEY then do nothing
                            break;
                    }
                }
            }
            finally
            {
                sck.Close();
                NCurses.EndWin();
            }
        }
      
    }
}