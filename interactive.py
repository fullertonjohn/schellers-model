import streamlit as st
import numpy as np
import random
import time

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Schelling's Model", layout="wide")
st.title("Interactive Schelling's Model")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Parameters")

# Grid settings
GRID_SIZE = st.sidebar.slider("Grid Size", 10, 100, 100)
EMPTY_HOUSE_RATIO = st.sidebar.slider("Empty House Ratio", 0.01, 0.5, 0.1)
BLUE_PARTY_RATIO = st.sidebar.slider("Blue Party Ratio", 0.1, 0.9, 0.5)
RELOCATION_THRESHOLD = st.sidebar.slider("Relocation Threshold", 0.0, 1.0, 0.4)
# Speed slider
ANIMATION_SPEED = st.sidebar.slider("Animation Speed (Delay)", 0.0, 0.5, 0.0)

# Derived constants
RED_PARTY_RATIO = 1 - BLUE_PARTY_RATIO
BLUE_EFFECTIVE_RATIO = (1 - EMPTY_HOUSE_RATIO) * BLUE_PARTY_RATIO
RED_EFFECTIVE_RATIO = (1 - EMPTY_HOUSE_RATIO) * RED_PARTY_RATIO

# Integer constants
EMPTY = 0
BLUE = 1
RED = 2

# --- YOUR EXACT ALGORITHM FUNCTIONS (UNCHANGED) ---

def identify(grid):
    unhappy_agents = []
    empty_spots = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            #tally neighbors
            if grid[row][col] != EMPTY:
                total_neighbors = 0
                bad_neighbors = 0
                for neighbor_row in range(max(0, row-1), min(GRID_SIZE, row+2)):
                    for neighbor_col in range(max(0, col-1), min(GRID_SIZE, col+2)):
                        if(neighbor_row != row or neighbor_col != col):
                            if(grid[neighbor_row][neighbor_col] != grid[row][col] and grid[neighbor_row][neighbor_col] != EMPTY):
                                bad_neighbors+=1
                            if grid[neighbor_row][neighbor_col] != EMPTY:
                                total_neighbors+=1
                if(not total_neighbors or bad_neighbors / total_neighbors > RELOCATION_THRESHOLD):
                    unhappy_agents.append((row,col))
            else: 
                empty_spots.append((row,col))
    return unhappy_agents, empty_spots

def relocate(grid_in, unhappy_in, empty_in):
   for agent in unhappy_in:
       destination = random.choice(empty_in)
       destination_r, destination_c = destination
       agent_r, agent_c = agent
       grid_in[destination_r][destination_c] = grid_in[agent_r][agent_c]
       grid_in[agent_r][agent_c] = EMPTY
       empty_in.remove(destination)
       empty_in.append(agent)

# --- INITIALIZATION ---

if 'grid' not in st.session_state:
    flat_grid = np.random.choice(
        [EMPTY, BLUE, RED],
        size = GRID_SIZE*GRID_SIZE,
        p=[EMPTY_HOUSE_RATIO, BLUE_EFFECTIVE_RATIO, RED_EFFECTIVE_RATIO]
    )
    st.session_state.grid = flat_grid.reshape(GRID_SIZE,GRID_SIZE)
    st.session_state.count = 0

# --- APP LOGIC ---

col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🎲 New Random Grid"):
        flat_grid = np.random.choice(
            [EMPTY, BLUE, RED],
            size = GRID_SIZE*GRID_SIZE,
            p=[EMPTY_HOUSE_RATIO, BLUE_EFFECTIVE_RATIO, RED_EFFECTIVE_RATIO]
        )
        st.session_state.grid = flat_grid.reshape(GRID_SIZE,GRID_SIZE)
        st.session_state.count = 0
    
    run_simulation = st.button("▶️ Run Simulation")
    status_text = st.empty()

with col1:
    plot_placeholder = st.empty()

# --- FAST RENDERER ---
def render_fast(grid):
    # Create an RGB image array (Height, Width, 3 Channels)
    h, w = grid.shape
    img = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Assign colors manually [Red, Green, Blue]
    img[grid == EMPTY] = [255, 255, 255]
    img[grid == BLUE] = [100, 149, 237] 
    img[grid == RED] = [250, 128, 114] 
    
    return img

# Display initial state (UPDATED PARAMETER HERE)
plot_placeholder.image(render_fast(st.session_state.grid), use_container_width=False, width=500, caption="Grid State")
status_text.write(f"Iteration: {st.session_state.count}")

# --- SIMULATION LOOP ---

if run_simulation:
    continue_loop = True
    
    while continue_loop:
        st.session_state.count += 1
        
        # Algorithm (Your Logic)
        unhappy, empty = identify(st.session_state.grid)
        
        if not unhappy:
            continue_loop = False
            st.success(f"Simulation finished after {st.session_state.count} iterations")
        else:
            status_text.write(f"Iteration: {st.session_state.count} | Unhappy agents: {len(unhappy)}")
            relocate(st.session_state.grid, unhappy, empty)
            
            # FAST RENDER (UPDATED PARAMETER HERE)
            plot_placeholder.image(render_fast(st.session_state.grid), use_container_width=False, width=500, caption="Grid State")
            
            if ANIMATION_SPEED > 0:
                time.sleep(ANIMATION_SPEED)