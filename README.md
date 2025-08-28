

# MemoryScape

## A 3D Garden for Your Digital Memories

MemoryScape is a full-stack application that transforms your digital memories (photos and videos) into a beautiful, interactive 3D garden. The project allows users to bring their memories to life, giving them a tangible and emotionally engaging way to revisit their past.

Every memory is represented as a unique flower in a serene, 3D environment. Users can navigate this garden and interact with the flowers to reveal a holographic display of the memory—a photo or video from that moment in time.

## Key Features

  * **Interactive 3D Environment:** An immersive and responsive 3D garden where memories are visualized as flowers.
  * **Holographic Memory Display:** Clicking on a flower reveals a floating holographic screen to display the associated photo or video.
  * **User-Friendly Dashboard:** A simple admin interface for creating, managing, and organizing your memories.
  * **Scalable Backend:** A robust API to handle memory data and serve content to the frontend.

## Under the Hood

The application is built using a modern and powerful technology stack.

**Frontend:**

  * **React:** For a component-based and efficient user interface.
  * **Three.js / React-Three-Fiber:** To render and manage the immersive 3D scene.

**Backend:**

  * **FastAPI:** A high-performance Python web framework for a fast and reliable API.

**Database:**

  * **SQLite:** A lightweight, serverless database for persistent data storage.

## Getting Started

Follow these steps to get a copy of the project up and running on your local machine.

### Prerequisites

You will need the following installed on your machine:

  * Python 3.x
  * Node.js & npm (or yarn)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/[Your_Username]/MemoryScape.git
    cd MemoryScape
    ```

2.  **Set up the backend:**

    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3.  **Set up the frontend:**

    ```bash
    cd ../frontend
    npm install
    ```

### Running the Application

1.  **Start the backend server:**
    Open a new terminal, navigate to the `backend` directory, and run:

    ```bash
    uvicorn server:app --reload localhost 8000
    ```

2.  **Start the frontend development server:**
    Open another terminal, navigate to the `frontend` directory, and run:

    ```bash
    npm start
    ```

The application should now be running and accessible at `http://localhost:8000`.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE.md` for more information.

-----

**Thank you for your interest in MemoryScape\!**
