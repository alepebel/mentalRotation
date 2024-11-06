#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Alexis Perez-Bellido, 10/2024
# Code for Attention & Perception mental rotation task. 
# Con este código podrás cambiar el tamaño de las letras, la distancia a la que aparecen, los ángulos a testear
# Los resultados quedarán guardados en un documento CSV

from psychopy import visual, logging, core, event,  gui, data, clock
from psychopy.hardware import keyboard

import random
import numpy as np
import pandas as pd

expInfo = {}
subjInfo = {'observer':'test',  'gender (H/M/Other)': '?', 'age': 0, 'hand (L/R)': '?'}    

test_trials = 'no' # if 'yes' only 5 trials will be presented

date = data.getDateStr(format="%Y-%m-%d-%H%M")

# present a dialogue to change params
sdataDlg = gui.DlgFromDict(subjInfo, title='Práctica de Rotación Mental', order = [ 'observer','gender (H/M/Other)', 'age', 'hand (L/R)']) 
fileName = subjInfo['observer']
fileName = fileName+'_'+ date # the extension is required in order to be read by pyshcophy wrapper function "fromFile"

if sdataDlg.OK:  # or if ok_data is not None
    print('vamos!')
else:
    print('User cancelled')
    core.quit()

# Create a window
win = visual.Window(fullscr=1) # si pones esto dentro del parentesis y quitas fullscre veras una pantalla mas pequeña [800, 600]
win.mouseVisible = False 
# Define the letter "R"
size = 0.2
letter_left = visual.TextStim(win, text='R', height=size)
letter_right = visual.TextStim(win, text='R', height=size)

# Distance between the letters and the center (0 is center, 1 at the edge of screen)
disparity = 0.25

# Define the possible rotation angles
angles = [0, 45, 90, 135, 180, 225, 270, 315]

# Define the possible versions (same or different)
trial_types = ['same', 'different']

# Define the possible versions (same or inverted)
versions = ['normal', 'inverted']


# Define how many times each combination will be repeated
trial_reps = 6

# Create the combinations of experimental conditions
stimList = []
for trial_type_idx in trial_types:
    for angle_diff_idx in angles:
            stimList.append({'trial_type': trial_type_idx, 'angle_diff': angle_diff_idx}) # combinations of conditions


# generate trials vector
trials = data.TrialHandler(stimList, trial_reps , method='random')
nTrials = trials.nTotal

# Fixation point
fp_point = visual.Circle(win,radius=5,pos=[0,0],fillColor='red', units= 'pix') #
fixation_time = 0.5 # waith half a second before the characters are presented

# Instructions
instructions = visual.TextStim(win, text='Pulsa "s" si las letras en ambos lados son iguales y  "d" si son differentes.', pos=(0.0, 0.1))
instructions.draw()
next_instruction = visual.TextStim(win, text='Cuando estes preparad@, pulsa las barra espaciadora para continuar.', pos=(0.0, -0.2), color='blue', height=0.05)
next_instruction.draw()

win.flip()

event.waitKeys(keyList=['space'])
trialClock = clock.Clock()  # if this doesn't work for some reason use core.Clock() instead
kb = keyboard.Keyboard(clock=trialClock)

# Initialize data storage
data_matrix = []

# Run the experiment
for  n_trial, thisTrial in enumerate(trials): 
    
    
    diff_angle =  thisTrial['angle_diff'] 
    trial_type = thisTrial['trial_type'] 
    # pick randonly the version
    version = random.choice(versions)

    # determine the angles for the different stimuli
    ref_angle = random.choice(angles)
    angle = ref_angle + diff_angle

    
    if version == 'inverted':
        letter_left.text = 'Я'  # Inverted R
        letter_right.text = 'Я'  # Inverted R
    else:
        letter_left.text = 'R'  # Inverted R
        letter_right.text = 'R'  # Inverted R
        

    if trial_type == 'different':
        diff_characters = ['R', 'Я']
        random.shuffle(diff_characters)    
        letter_left.text =  diff_characters[0]  
        letter_right.text = diff_characters[1] 
    
    # Draw the fixation point
    fp_point.draw()
    win.flip()
    core.wait(fixation_time)
    kb.clearEvents()  # clear buffer keyboard

   
    letter_left.ori = ref_angle
    letter_left.pos = (-disparity, 0) # shift to the left
    letter_left.draw()

    letter_right.ori = angle
    letter_right.pos = (disparity, 0) # shift to the right
    letter_right.draw()

    fp_point.draw()
    win.flip()
    

    start_time = trialClock.getTime() 
    
    thisResp = None
    while thisResp == None:
        keys = kb.getKeys()
        for thisKey in keys:
            if thisKey=='q':  # it is equivalent to the string 'q'
                core.quit()
            if thisKey=='s' or thisKey=='d':
                thisResp = thisKey.name
                
                #print(thisKey.name, thisKey.tDown, thisKey.rt)
            #else:
            #    print(thisKey.name, thisKey.tDown, thisKey.rt)
    kb.clearEvents()  

    rt = thisKey.rt - start_time
    #response = event.waitKeys(keyList=['s', 'i'])

    correct = None
    
    if (thisResp == 's' and trial_type == 'same') or (thisResp == 'd' and trial_type == 'different'):
        feedback = visual.TextStim(win, text='Correcto!', color='green')
        correct = 1
    else:
        feedback = visual.TextStim(win, text='Incorrecto!', color='red')
        correct = 0
    print(rt)
    feedback.draw()
    win.flip()
    core.wait(1) # feedback time
    kb.clearEvents()

    # Save the trial data to matrix
    trial_data = [subjInfo['observer'], subjInfo['gender (H/M/Other)'], subjInfo['age'],subjInfo['hand (L/R)'], n_trial + 1, ref_angle, diff_angle, version, letter_left.text, letter_right.text, trial_type, thisResp, rt, correct]
    data_matrix.append(trial_data)

    data = pd.DataFrame(data_matrix, columns=['subj', 'gender', 'age', 'hand', 'trial', 'ref_angle', 'diff_angle', 'version', 'letter_left', 'letter_right', 'trial_type', 'response', 'rt', 'correct'])
    data.to_csv('mental_rotation.csv', index=False)

    if (n_trial == 5) & (test_trials == 'yes'):
        break
    
print('fin')
win.flip()
win.mouseVisible = True
core.wait(3)



# Close the window
win.close()
core.quit
