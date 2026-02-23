# Funky Radical Electrodynamics Engine 1105 #

This Project (which can be abbreviated to FREE1105) Will Exist in 5 Phases:

1) Set Up the Electric Fields in a 2D Coordinate System
2) Simulate the Motion of Electric Point Charges
3) Simluate the Motion of Charged Rigid Bodies
4) Visualise the Field via Geometrical Curvature
5) Implement Maxwell's 4th Law for Magnetic Fields and Light

just download the folder and run the Jyptiter notebook to see each phase OR just run the main py

Or at least this was the Phase plan initially, but i only really did the first 2 phases unfortunately due to time restraints and my degree kicking me!!

## What actually happened and Key Takeaways

The UI was cumbersome to build and HEAVILY vibe coded - however the maths and physics was done mostly mannually and development of the approach was done for the sake of numerical stability. Initially I implemented an euler integrator which obviously blew up regarding energy conservation. Then switched to a RK2 then RK4, which was so much smoother. Then, due to a genuine interaction where a peer saw me working on my simulator, he suggested by the grace of God to check out symplectic integrators for the purpose of energy conservation. This was the final approach used and, while not perfectly, it conserves energy the best. To diagnose this process, I tracked total KE and PE and what happened was this would oscillate around an equilibrium as opposed to explosions and dead stops.

Furthemore, separate to the physics - I gained a lot of experience in making intuitive useful GUIs. Also i had to learn a lot of class discipline and encapsulation because although vision wise i was very strategic and progression based, the actual code architecture was extremely on the fly. 
