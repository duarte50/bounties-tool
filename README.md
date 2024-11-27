# Bounties Tool

Inspired by **RouteFinder** ([RouteFinder](https://brighter-shores-routefinder.com/)), the **Bounties Tool** is an in-game overlay for Brighter Shores that reads the game screen to find the quickest path to complete any set of bounties. This tool only requires a click a button to automatically find the most efficient route for your current bounties. While still a WIP, I’ve made it available in its current state to allow more users to test, provide feedback, and contribute to the project.

---

## How it works

1. **Fullscreen the game**: First, make sure the game is in fullscreen mode.
2. **Open the Left Menu**: Open the Left Menu and place the Bounties Menu in the top corner. Resize the Left Menu to the smallest possible size while ensuring the Bounties Menu is not cramped (see reference image below).
3. **Grab the Bounties**: Retrieve the bounties from the Merchant Guild and click the **Run** button to find the optimal path.

Alternatively, you can place the Bounties Menu in the Right Menu, but you will need to adjust the values in the Region Input.

## What value should I use in Region Input?

Region Input is the coordinates on screen where your bounties are, if you are using a single Full HD monitor this value will probably be ```0,50,100,500```, but you can test with different values.

---

## Observations

- **"X bounty is not available."**
  This happens because information for most bounties above level 200 is missing. While I couldn't include these in the program, you can manually update the `app/data/bounties_data.json` file by adding the buyer for that bounty. After that add a screenshot of the bounty to the `assets/bounties` folder (following the image template below). Once updated, the tool will automatically recognize these bounties.

- **"The tool cannot find the bounties."**
  Ensure the **Region Input** is set correctly. You can test this by clearing the Region Input (setting it to blank). If the tool still doesn't find your bounties, you can replace the images in `assets/bounties` with your own (following the image template below). This allows you to adjust the size and positioning of the **Bounties Menu** as needed.

- **"Is this bannable or against the rules?"**
  In-game overlays are not prohibited by the game’s rules. Overlays such as **Alt1 Toolkit** are widely used in RuneScape, so this tool should not result in a ban.

- **"Why are the routes different from those in RouteFinder?"**
  The algorithm used in this tool is a modified version of the one found on the RouteFinder website. Unlike RouteFinder, which can finish a route anywhere, this tool prioritizes completing routes at the **Merchant's Guild**.

---

## Running the project

Follow these steps to get the project up and running on your local machine.

1. Clone the Repository

```bash
git clone https://github.com/duarte50/bounties-tool.git
```

2. Set up the virtual environment

```bash
cd bounties-tool
python -m venv venv
```

3. Activate the virtual environment:

- **Windows**:

```bash
.\venv\Scripts\activate
```

- **macOS/Linux**:

```bash
source venv/bin/activate
```

3. Install required dependencies

```bash
pip install -r requirements
```

4. Run the Project

To run the project, simply execute the main Python file:

```bash
python app/main.py
```

5. (Optional) Build the executable

```bash
pyinstaller --onefile --noconsole --add-data "assets/bounties;assets/bounties" --add-data "app/data;app/data" app/main.py
```
