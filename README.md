# HotelReservationSystem

Class project for UCF's Processes for Object Oriented Software Development

## Teammates
- [Henrique Cury](https://github.com/HCury)
- [Rodrigo Lopez](https://github.com/RodiLop)
- [Brian Pelo](https://github.com/Brianpelo)
- [Nicolas Soto](https://github.com/nsoto0216)

## Running the website locally
This system runs on Python 3.7

Start off by cloning the repo:  
`git clone https://github.com/danielzgsilva/HotelReservationSystem`

Navigate to the project root

If you use anaconda, you should install dependencies to a conda environment like so:  
`conda env create -f environment.yml`

To activate the environment:  
`conda activate hotel_env`

If you have trouble creating the env with the yml, you can do so manually like this:  
`conda create --name <env_name>`  
`conda activate <env_name>`  
`conda install flask`  
`conda install sqlite`  

To list all packages in the environment
`conda list`

Deactivate the environment
`conda deactivate`

Run the app with:  
`python app.py`

The project will then serve locally on port 5555:  
`http://localhost:5555/`
