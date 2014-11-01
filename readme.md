# Flier

I got a [Crazyflie](http://wiki.bitcraze.se/projects:crazyflie:index) for my birthday.

This is my attempt at building something that lets me control it using the [nanoKontrol2](http://www.korg.com/us/products/controllers/nanokontrol2/) that I happened to have at home.

## Requirements

Reading values from the nanoKontrol2 requires python-rtmidi to be installed.

## Controlling the Crazyflie

The different functions of the Crazyflie have been mapped to the following on the nanoKontrol2:

* Thrust: The leftmost rotating knob
* Roll: The leftmost slider
* Pitch: The second slider
* Yaw: The third slider

```
        ---                                        ___        
       /                       CxD                    \       
       | -Yaw                   |                 +Yaw |      
       V       Green_________________________ Blue     V      
                   |+Roll                    |                
                   |                         |                
                   |                         |                
                O  |                         |  O             
                X--|+Pitch            -Pitch |--X             
                U  |                         |  U             
                   |                         |                
                   |                         |                
                   |-Roll                    |                
                   |_________________________|                
                Red             |                             
                               CxD                            
```