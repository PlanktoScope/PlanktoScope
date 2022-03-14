# Debug (Problem Solving)


## Known problem

1. My Node-red interface is poorly organized.

    * The 1st potential problem is that your computer résolution is too different than the classical. To solve this probleme zoom out or in on your web-page (Internet browser). To do this go to seeting of your navigator and find zoom or use shrtcut `ctrl + "-" or ctrl + "+"`. Until you get on the **Home** page, in **beginner mode**, the **Shutdown** section at the end of the first line (like picture bellow).

    <br/>![Debug](modification/home_page.webp)

    * The 2nd potential problem is that you think there are too many groups. It’s possible, it’s because there is a bug between beginner and expert mode. You need to go to page `Home`, click on **UNLOCK EXPERT MODE** and then activate **expert mode**. And if you want to use the planktoscope in beginner mode, click on **beginner mode** (make a back and forth).  

2. My motors don't work when I ask them to.

    - If pump and focus motors don't work. Check if they are supplied. To do this you need to see a **green LED** on the motor Hat.
    
    - If focus motor operating but no the pump motor, you don't get enough power from your power supply.  

3. I don't have GPS data on my Node-red interface.

    * If there is no led power on in GPS hat, that means the GPS is not alimented, try to push on the nat or check raspberry alimentation.
    
    * If the led is blinking, check the antenna connection. If it don't work, it is possible that your Gps hat don't see satelite (ex: to many cloud in the sky)

4. My PlanktoScope say `cut the power in 5s` when I didn't turn it off **or** the stream of camera is not display.

    * Somethink was wrong, go to page `Administration` and clik on restart **RESTART PYTHON**.

    * If is not work, try to restart your machine, go to page `Administration` and clik on **REBOOT**.

    * If it still doesn't work after reboot, you need to restor the file **hardware.json**. For that go to [ssh connection](Make_your_modification.md#start-coding), then go in folder **Planktoscope** and write this line to reset the file.

            git checkout -- hardware.json


5. I use the PlanktoScope with the Node-red interface but the PlanktoScope does nothing.

    * It's possible, the node-red can be here like gosth but in background there are nothing. If you refresh the page and you see no connection, check that the PlanktoScope is turn on and check that your computer and the PlanktoScope are connected to a same network. 
    
    * Check your wifi connection if you are in direct wifi or search ip of your PlanktoScope with angry scanner [tuto](Make_your_modification.md#start-coding).

6. I can't fin the wifi of my PlanktoScope in wifi setting of my computer.

   * If ne name of planktoscope is not display on fan hat and you see **Cut the power in 5s** you need to restart it.
  
   * After starting it, the wifi emmission can take few minute. Please be patient.
  
   * Make sure that your PlanktoScope is not connect to a other  wifi network. 

7. I don't fin the PlanktoScope IP when I scan my wifi network

    * Network bug can be arrived, and the PlanktoScope can disconnect. It will try to re-connect and it does not arrive, it will start difusion of her wifi. Please check available wifi connections and retry.
  
    * You entered the wrong passwords when you registered the network on the node red interface. No worries, the PlanktoScope will be difuse is wifi network. When it's done, you can return to the page `Ẁifi` on node red interface and add the network with right password. The previons will be replace.
  
8. I start segmentation but it take to much time and I want to stop it. 
    * For the time being, there is no button to stop segmentation.

    * The only way to do this without all break, is to **reboot** on page `Administration`. The means allow to kill all threads with a signal, there will stop properly.
  
9. The planktoScope make noise when it's turn on.
  
    * The fan can be make noise, to resolve this problem,  press shortly on this one to re-align it.

## Others informations

- Leds informations :

    1. Led of motor hat

        The motor hat led, is turn on green if the module is correctly supply.

    1. Led of Gps hat

        There are 2 status for this led, the first one, led is `blinking red`, this status means that the hat is supply but it had **not yet fix gps satellite**. The second one, led is `fixed red`, this status means that the hat **found enough of satelite** and usually it should send position and time to node-red.


    2. Leds of fan hat

        | Color  | Motion    | Meaning                              |
        | :------|:---------:| :------------------------------------|
        | <span style="color: green"> Green </span> | Fixed     | Soft is in progress of start or an error of start if during to much |
        | <span style="color: Blue"> Blue </span>   | Fixed     | Device is ready, properly started  |
        | <span style="color: Blue"> Blue </span>   | Blinking  | Pump is running |
        | <span style="color: Red"> Red </span>    | Fixed     | An error has occurred |
        | <span style="color: Yellow"> Yellow </span> | Blinking  | The system was interrupted |
        | <span style="color: Purple"> Purple </span> | Fixed     | The segmenter is in progress|
        | <span style="color: Purple"> Purple </span> | Blinking  | Optic motors (focus) are running |
        | White  | Ficed     | Immaging in progress |


- File organization

    Go to the good section with this link [File organization](Make_your_modification.md#file-organization)

- Code organization

    Go to the good section with this link [Code organization](Make_your_modification.md#code-organization)


