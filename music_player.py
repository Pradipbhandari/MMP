import os
import random
import shutil
import time
import threading
import boto3
import pygame 
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import tkinter as tkr 
from tkinter.filedialog import askopenfilename 
from ttkthemes import themed_tk as tk
import tkinter.ttk as ttk
from dotenv import load_dotenv
load_dotenv()


#access keys and secrets
access_key = os.getenv('ACCESS_KEY')
access_secret =os.getenv('ACCESS_SECRET')
bucket_name = os.getenv('BUCKET_NAME')



#Create S3 client and connect
try: 
    s3_client = boto3.client('s3',aws_access_key_id=access_key,aws_secret_access_key=access_secret)
except:
    print("Check your internet connection or credentials")


# default variables
user_emotion = "happy"
user_emo = ''
listofsongs = []
index = 0
current_dir = os.getcwd()
default_dir = current_dir+'\\songs\\happy'
state_mute = False
global stopped
stopped = False
global pause
pause = False
def check_folders():
    song_folders = ['happy','sad','neutral','disgust','scared','surprised','angry']
    if(os.path.exists(current_dir+'\\songs')):
        # print('yes bro')
        for folder in song_folders:
            if os.path.exists(current_dir+"\\songs\\"+folder):
                # print('no need')
                continue
            else:
                os.makedirs(current_dir+"\\songs\\"+folder)
        
    else:
        os.makedirs(current_dir+'\\songs')
        for folder in song_folders:
            os.makedirs(current_dir+"\\songs\\"+folder)

check_folders()

def slide(x):
    pygame.mixer.music.load(listofsongs[index])
    pygame.mixer.music.play(loops=0, start=music_slider.get())

def counter_mood():
    global user_emotion
    if user_emo == 'happy':
        user_emotion = 'neutral'
        return user_emotion
    elif user_emo == "sad":
        user_emotion = 'happy'
        return user_emotion
    elif user_emo == 'neutral':
        user_emotion = 'surprised'
        return user_emotion
    elif user_emo == 'surprised':
        user_emotion = 'scared'
        return user_emotion
    elif user_emo == 'scared':
        user_emotion = 'happy'
        return user_emotion
    elif user_emo == 'disgust':
        user_emotion = 'neutral'
        return user_emotion
    elif user_emo == 'angry':
        user_emotion = 'neutral'
        return user_emotion

def add_song(path):
    mood_var.set("Uploading Files...")
    song_full_path = askopenfilename(
        initialdir=current_dir, title="Choose " + path + " Songs ", filetypes=(("mp3 files", "*.mp3"),))
    song = song_full_path.split('/')[-1]
    # print(current_dir)
    print(song)
    
    try:
        s3_client.upload_file(song_full_path,bucket_name,path+"/"+song)
        mood_var.set("Upload Complete.")
        print('done')
    except Exception as e:
        mood_var.set("Error occured. Please check your internet connection or try again later.")
        print(e)
    try:
        shutil.copy(song_full_path, current_dir+'\\songs\\'+path+'\\'+song)
    except:
        print('Songs present in the given folder')

def initialize_music(directory):
    global index
    # print(directory)
    os.chdir(directory)
    song_list = os.listdir()
    listofsongs.clear()
    play_list.delete(0, tkr.END)
    for files in os.listdir(directory):
        # only add files with mp3 extension
        if (files.lower().endswith(".mp3")):
            realdir = os.path.realpath(files)
            audio = ID3(realdir)
            listofsongs.append(files)
    song_list.reverse()
    for item in song_list:
        pos = 0
        play_list.insert(pos, item)
        pos += 1
    play_list.pack(fill="x")
    play_list.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=play_list.yview)
    pygame.init()
    pygame.mixer.init()
    try:
        index = random.randint(0, len(listofsongs)-1)
        # load the first song
        pygame.mixer.music.load(listofsongs[index])
    except:
        print("error")

def play_time():
    global index
    if stopped:
        return
    global song
    current_time = pygame.mixer.music.get_pos()/1000

    # print(time.gmtime(current_time))
    converted_current_time = time.strftime(
        '%H:%M:%S', time.gmtime(current_time))

    # current_song = play_list.curselection()
    song = listofsongs[index]
    # print(song, 'name')

    song = f'{current_dir}/songs/{user_emotion}/{song}'
    # print(song, 'emo')
    song_mut = MP3(song)
    global song_length
    song_length = song_mut.info.length

    converted_song_length = time.strftime('%H:%M:%S', time.gmtime(song_length))
    current_time += 1
    # print(music_slider.get(), int(song_length))
    if(int(music_slider.get()) == int(song_length)):
        print('oe')
        status_bar.config(
            text=(f'{converted_song_length}|{converted_song_length}'))
        if(index == len(listofsongs)-1):
            index = -1
            nextsong()
        else:
            # index+=1
            nextsong()

    elif pause:
        pass
    elif(int(music_slider.get()) == int(current_time)):
        slider_position = int(song_length)
        music_slider.config(to=slider_position, value=int(current_time))
    else:
        slider_position = int(song_length)
        music_slider.config(to=slider_position, value=int(music_slider.get()))

        converted_current_time = time.strftime(
            '%H:%M:%S', time.gmtime(int(music_slider.get())))

        status_bar.config(
            text=(f'{converted_current_time}|{converted_song_length}'))

        next_time = int(music_slider.get())+1
        music_slider.config(value=next_time)

    # status_bar.config(
    #     text=(f'{converted_current_time}|{converted_song_length}'))
    # music_slider.config(value=int(current_time))

    status_bar.after(1000, play_time)

def setDirectory(user_emo):
    print(counter_mood())
    if user_emo == "happy":
        return os.path.join(current_dir, 'songs\\'+counter_mood())
    elif user_emo == "sad":
        return os.path.join(current_dir, 'songs\\'+counter_mood())
    elif user_emo == "surprised":
        return os.path.join(current_dir, 'songs\\'+counter_mood())
    elif user_emo == "angry":
        return os.path.join(current_dir, 'songs\\'+counter_mood())
    elif user_emo == "scared":
        return os.path.join(current_dir, 'songs\\'+counter_mood())
    elif user_emo == "disgust":
        return os.path.join(current_dir, 'songs\\'+counter_mood())
    elif user_emo == "neutral":
        return os.path.join(current_dir, 'songs\\'+counter_mood())

    else:
        print("The requested emotion based songs are currently unavailable. Please choose either Happy, Sad, Calm or Energetic if interested!")

# fumction to update our label as the song changes or updates
def updatelabel():
    global index
    var.set('Now Playing :'+listofsongs[index])

def directorychooser(directory):
    global play_list
    play_list.delete(0, tkr.END)
    initialize_music(directory)
    updatelabel()
    play()

def setvol(x):
    global state_mute
    # global previous_slider
    # global previous_vol

    # previous_slider = volume_slider.get()
    volume = 1 - int(volume_slider.get())/100  # typecasting(string into int)
    pygame.mixer.music.set_volume(volume)
    # print(volume_slider.get())
    if(volume_slider.get()==100):
        volume_button['image'] = volumeImage
        state_mute == True
    elif(volume_slider.get()<100):
        volume_button['image'] = muteImage
        state_mute == False


    

def vol_mute():
    global state_mute
    global previous_slider
    if (state_mute == False):
        pygame.mixer.music.set_volume(0)
        previous_slider = volume_slider.get()
        volume_slider.set(100)  # the slider has value 100 at 0 volume
        volume_button['image'] = volumeImage
        state_mute = True
        # print('anuj', volume_slider.get())
    elif(state_mute == True):
        pygame.mixer.music.set_volume(0.5)  # hardcoding volume when unmuting
        volume_slider.set(50)
        volume_button['image'] = muteImage
        state_mute = False
        # print('timsina', volume_slider.get())

def nextsong():
    # get index from gloabl
    global index
    global pause
    pause = False
    resumebutton['image'] = pausephoto
    music_slider.config(value=0)
    # increament index
    index += 1
    if(index == len(listofsongs)):
        index = 0
    else:
        index= index
    pygame.mixer.music.load(listofsongs[index])
    pygame.mixer.music.play(loops=0)
    updatelabel()

def prevsong():
    global index
    global pause
    pause = False
    resumebutton['image'] = pausephoto
    # status_bar.config(text='')
    music_slider.config(value=0)
    index -= 1
    if(index ==-1):
        index = len(listofsongs)-1
    pygame.mixer.music.load(listofsongs[index])
    pygame.mixer.music.play(loops=0)
    updatelabel()

def stop():
    global pause
    pause = False
    resumebutton['image'] = pausephoto
    status_bar.config(text='')
    music_slider.config(value=0)
    # stop the current playing song
    pygame.mixer.music.stop()
    # set our label to empty
    var.set("")
    global stopped
    stopped = True

def download():
    mood_var.set('Syncing song from cloud.')
    try:
        keys = s3_client.list_objects(Bucket = bucket_name)
    except:
        mood_var.set("Couldn't Sync Song Please Check Your Bucket.")
    try:
        for key in keys['Contents']:
            filename = key['Key'].split('/')
            if(filename[-1]) in os.listdir(current_dir+"\\songs\\"+filename[0]):
                # print('song is present no need to download')
                continue
            else:
                s3_client.download_file(bucket_name,key['Key'],os.path.join(current_dir,"songs\\"+key['Key']))
                
        mood_var.set('Synced song from cloud.')
        # mood_var.set("Here are Your "+user_emotion+" Songs.")      
    except:
        mood_var.set("Seems like your cloud is empty.")

def play():
    global stopped
    stopped = False
    global index
    status_bar.config(text='')
    music_slider.config(value=0)
    print(index)
    item_index = play_list.curselection()
    print(item_index)
    try:
        index = item_index[0]
        print('here waala')
    except:
        index = index
    print(index)
    print(listofsongs)
    pygame.mixer.music.load(listofsongs[index])
    pygame.mixer.music.play(loops=0)
    play_time()

    updatelabel()

def pause_play(is_pause):
    global pause
    pause = is_pause

    if(pause):
        resumebutton['image'] = pausephoto
        pygame.mixer.music.unpause()
        pause = False
    else:
        resumebutton['image'] = resumephoto
        pygame.mixer.music.pause()
        pause = True

def rescan():
    global user_emo
    import real_time_video
    # from real_time_video import
    user_emo = real_time_video.face_detection()
    mood_var.set("You seem like you have "+user_emo +
                 " mood lets play you a " + counter_mood()+" song.")
    dir_String = setDirectory(user_emo)
    directorychooser(dir_String)

def get_songs(emotion):
    global pause
    pause = False
    resumebutton['image'] = pausephoto
    global user_emotion
    status_bar.config(text='')
    music_slider.config(value=0)
    user_emotion = emotion
    # dir_String = setDirectory(emotion)
    directorychooser(os.path.join(current_dir,'songs/'+emotion))
    mood_var.set("Here are your "+emotion+" songs.")
    

# Creates an object for the ThemedTk wrapper for the normal Tk class
music_player = tk.ThemedTk()
music_player.title("MMP - Mood Music Player")
music_player.iconbitmap("ico.ico")
# music_player.iconbitmap(r'title.ico')
music_player.geometry("580x580")

my_menu = tkr.Menu(music_player)
music_player.config(menu=my_menu)

playList_menu = tkr.Menu(my_menu)
my_menu.add_cascade(label="Playlists", menu=playList_menu)

playList_menu.add_command(
    label='Happy Songs', command=lambda: get_songs('happy'))
playList_menu.add_command(label='Sad Songs', command=lambda: get_songs('sad'))
playList_menu.add_command(label='Scared Songs',
                          command=lambda: get_songs('scared'))
playList_menu.add_command(label='Surprised Songs',
                          command=lambda: get_songs('surprised'))
playList_menu.add_command(label='Disgusting Songs',
                          command=lambda: get_songs('disgust'))
playList_menu.add_command(
    label='Angry Songs', command=lambda: get_songs('angry'))
playList_menu.add_command(label='Neutral Songs',
                          command=lambda: get_songs('neutral'))

add_song_menu = tkr.Menu(my_menu)
my_menu.add_cascade(label="Add songs", menu=add_song_menu)

add_song_menu.add_command(label='Add Happy Songs',
                          command=lambda: (add_song('happy')))
add_song_menu.add_command(label='Add Sad Songs',
                          command=lambda: add_song('sad'))
add_song_menu.add_command(label='Add Scared Songs',
                          command=lambda: add_song('scared'))
add_song_menu.add_command(label='Add Surprised Songs',
                          command=lambda: add_song('surprised'))
add_song_menu.add_command(label='Add Disgusting Songs',
                          command=lambda: add_song('disgust'))
add_song_menu.add_command(label='Add Angry Songs',
                          command=lambda: add_song('angry'))
add_song_menu.add_command(label='Add Neutral Songs',
                          command=lambda: add_song('neutral'))


# Making a mood Label
mood_var = tkr.StringVar()
mood_label = tkr.Label(music_player, font="TimesNEwRoman 12",
                       textvariable=mood_var, bg="white", fg="black", height=2, justify='left',relief=tkr.GROOVE, bd=2)

mood_label.pack(fill='x')

play_list = tkr.Listbox(music_player, font="TimesNewRoman 13 ", bg="white", fg="#191919",
                        selectmode=tkr.SINGLE, justify="left", height=15, bd='3px', selectbackground='#65c2f5', activestyle='none')

scrollbar = tkr.Scrollbar(music_player)
scrollbar.pack(side=tkr.RIGHT, fill=tkr.Y)

initialize_music(default_dir)
mood_var.set("Here's Your Happy song")
download_thread = threading.Thread(target = download, name='download')
download_thread.start()

var = tkr.StringVar()
song_title = tkr.Label(music_player, font="TimesNEwRoman 12 bold",
                       textvariable=var, bg="#979dac", fg="white", height=2, justify='left',wraplength=550,relief=tkr.GROOVE)
# , width=3, height=2, font="Helvetica 10 bold", text="Play", bg="yellowgreen/MediumTurquoise", fg="white"
# status bar
status_bar = tkr.Label(music_player, text='00:00:00|00:00:00', bd=1,
                        anchor=tkr.E,width=560,padx=10)
music_slider = ttk.Scale(music_player, from_=0, to=100,
                         orient=tkr.HORIZONTAL, value=0, command=slide, length=500)

volume_slider = ttk.Scale(music_player, from_=0, to=100,
                          orient=tkr.VERTICAL, value=50, command=setvol, length=80)


prevphoto = tkr.PhotoImage(file=current_dir+"/icons/previous.png")
prevbutton = tkr.Button(music_player, image=prevphoto,
                        width=32, command=prevsong)
# prevbutton.grid()


playphoto = tkr.PhotoImage(file=current_dir+"/icons/play-button.png")
playbutton = tkr.Button(music_player, image=playphoto, command=play)
# playbutton.grid()

stopphoto = tkr.PhotoImage(file=current_dir+"/icons/stop.png")
stopbutton = tkr.Button(music_player, image=stopphoto, command=stop)
# stopbutton.grid()


pausephoto = tkr.PhotoImage(file=current_dir+"/icons/pause.png")
resumephoto = tkr.PhotoImage(file=current_dir+"/icons/resume.png")
resumebutton = tkr.Button(music_player, image=pausephoto,
                          command=lambda: pause_play(pause))
# resumebutton.grid()


nextphoto = tkr.PhotoImage(file=current_dir+"/icons/next.png")
nextbutton = tkr.Button(music_player, image=nextphoto, command=nextsong)
# nextbutton.grid()


rescanPhoto = tkr.PhotoImage(file=current_dir+"/icons/face-scan.png")
rescanButton = tkr.Button(music_player, image=rescanPhoto, command=rescan)

# rescanbutton.grid()

volumeImage = tkr.PhotoImage(file=current_dir + "/icons/volume.png")
muteImage = tkr.PhotoImage(file=current_dir + "/icons/mute.png")
volume_button = tkr.Button(music_player, image=muteImage, command=vol_mute)
# volume button grid

song_title.pack(fill="x", ipadx=5, ipady=2)
volume_slider.pack(side='right',padx=20)

music_slider.pack()
status_bar.pack()
volume_slider.pack(side='right')
volume_button.pack(anchor="e", side="bottom")


# slider_label.pack(pady=10)

prevbutton.pack(side="left", padx=20)
playbutton.pack(side="left", padx=16)
stopbutton.pack(side="left", padx=16)
# pausebutton.pack(side="left", padx=16)
resumebutton.pack(side="left", padx=16)
nextbutton.pack(side="left", padx=16)
rescanButton.pack(side='left', padx=16)
# addSongs.pack(side="left",padx=16)
    


music_player.mainloop()



