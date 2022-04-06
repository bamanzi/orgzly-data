#!/usr/bin/env python3

import os.path
import sqlite3

def format_seconds_to_hhmmss(seconds):
    hours = seconds // (60 * 60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)


def export_to_org_format(sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    try:
        cur = conn.cursor()

        last_toplevel = ""
        for album in cur.execute('SELECT * FROM albums ORDER BY title'):
            # album: _id, title, director, last_played, cover_path
            album_id, album_title = album[0:2]

            toplevel = album_title[0:len("DW 2021-03")]
            if toplevel != last_toplevel:
                last_toplevel = toplevel
                print("* %s" % toplevel)
                
            print("** %s" % album_title)

            cur2 = conn.cursor()
            for audio_file in cur2.execute('SELECT * FROM audio_files WHERE album=? ORDER BY title',
                                           (album_id,)):
                # audio_file: _id, title, album, path, time, completed_time
                audio_file_id = audio_file[0]
                title = audio_file[1]
                time  = audio_file[4]
                completed_time = audio_file[5]

                state = 'TODO'
                if completed_time > 0:

                    if completed_time / time > 0.93:
                        state = 'DONE'
                    elif completed_time / time > 0.5:
                        state = 'HALF'
                    else:
                        state = 'START'

                title = os.path.splitext(title)[0]  # remove filename ext
                print("*** %s %s" % (state, title))
                print("")

                has_bookmarks = False
                cur3 = conn.cursor()
                for bookmark in cur3.execute('SELECT * FROM bookmarks WHERE audio_file=? ORDER BY position',
                                             (audio_file_id,)):
                    has_bookmarks = True
                    
                    # bookmark: _id, title, position, audio_file
                    bm_title = bookmark[1]
                    position = bookmark[2]
                    print("- %s (%s)" % (bm_title, format_seconds_to_hhmmss(position / 1000)))

                if has_bookmarks:
                    print("")                                                               

    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv)<2:
        print("Usage: %s audioanchror.db" % sys.argv[0])
        sys.exit(-1)
    
    export_to_org_format(sys.argv[1])
