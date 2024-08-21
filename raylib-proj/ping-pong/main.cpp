// GAME STEPS
// 1. create a blank screen and game loop
// 2. draw paddles and ball
// 3. move ball 
// 4. check for collisions with all edges
// 5. move player's paddle
// 6. move CPU paddle with AI
// 7. check for collisions with paddles
// 8. add scoring

#include <iostream>
#include <raylib.h>

Color green = Color{38, 185, 154, 255};
Color darkGreen = Color{20, 160, 133, 255};
Color lightGreen = Color{129, 204, 184, 255};
Color yellow = Color{243, 213, 91, 255};



int playerScore = 0;
int cpuScore = 0;

class Ball {
    public: 
        float x, y;
        int speedX, speedY;
        int radius;

        void Draw() {
            DrawCircle(x, y, radius, yellow);
        }

        void Update() {
            x += speedX;
            y += speedY;
            // ball bounces off walls
            if (y + radius >= GetScreenHeight() || y - radius <= 0) {
                speedY *= -1; // switches y-direction
            }

            // scoring
            if (x + radius >= GetScreenWidth()) {   // CPU scores
                cpuScore++;
                ResetBall();

            } 
            if(x - radius <= 0) { // player socres
                playerScore++;
                ResetBall();
            } 
        }
        
        // resets ball to center of the screen and resumes game
        void ResetBall() {
            x = GetScreenWidth()/2;
            y = GetScreenHeight()/2;

            int speedChoices[2] = {-1, 1};

            speedX *= speedChoices[GetRandomValue(0, 1)];
            speedY *= speedChoices[GetRandomValue(0, 1)];
        }     
};

class Paddle {
    protected:
        void LimitMovement() {      // prevents paddle from leaving screen

            if (y<= 0) {
                y=0;
            }
            if(y + height >= GetScreenHeight()) {
                y = GetScreenHeight() - height;
            } 
        }

    public:
        float x, y;
        float width, height;
        int speed;

        void Draw() {
            DrawRectangleRounded(Rectangle{x, y, width, height}, 0.8, 0, WHITE);
        }

        void Update() {
            if(IsKeyDown(KEY_UP)) {     // paddle moves up when up arrow is pressed
                y = y-speed;
            }
            if (IsKeyDown(KEY_DOWN)) {  // paddle moves down when down arrow is pressed
                y = y + speed;
            }

            LimitMovement();

        }
};

class CpuPaddle: public Paddle {
    public:
        void Update(int ballY) {
            if (y + (height/2) > ballY) {
                y = y - speed;
            } else if (y  + (height/2) <= ballY) {
                y = y + speed;
            }
            LimitMovement();
        }

};

Ball ball;
Paddle player;
CpuPaddle cpu;


int main () {
    std::cout << "starting the game!";

    const int screenWidth = 1280;
    const int screenHeight = 800;

    InitWindow(screenWidth, screenHeight, "My pong game!");
    SetTargetFPS(60); // speed of game, frames per second

    // initializing ball
    ball.radius = 20;
    ball.x = screenWidth/2;
    ball.y = screenHeight/2;
    ball.speedX = 7;
    ball.speedY = 7;

    // initializing player 
    player.width = 25;
    player.height = 120;
    player.x = screenWidth - player.width - 10;
    player.y = (screenHeight/2) - (player.height/2);
    player.speed = 6;

    // cpu or computer player
    cpu.width = 25;
    cpu.height = 120;
    cpu.x = 10;
    cpu.y = (screenHeight/2) - (cpu.height/2);
    cpu.speed = 6;

    
    // game loop
    while(WindowShouldClose() == false) {   // if esc or close icon is pressed
        BeginDrawing();                     // creates a blank canvas
        
        // Checking for collision
        if(CheckCollisionCircleRec(Vector2{ball.x, ball.y}, ball.radius, Rectangle{player.x, player.y, player.width, player.height})) {
            // collision with player paddle
            ball.speedX *= -1;
        }
        if(CheckCollisionCircleRec(Vector2{ball.x, ball.y}, ball.radius, Rectangle{cpu.x, cpu.y, cpu.width, cpu.height})) {
            ball.speedX *= -1;
        }
        // Updating
        ball.Update();
        player.Update();
        cpu.Update(ball.y);

        // Drawing
        ClearBackground(darkGreen);
        DrawRectangle(screenWidth/2, 0, screenWidth/2, screenHeight, green);
        DrawCircle(screenWidth/2, screenHeight/2, 150, lightGreen);
        DrawLine((screenWidth/2), 0, (screenWidth/2), screenHeight, WHITE);
        ball.Draw();
        cpu.Draw();
        player.Draw();

        DrawText(TextFormat("%i", cpuScore), (screenWidth/4) - 20, 20, 80, WHITE);
        DrawText(TextFormat("%i", playerScore), 3 * (screenWidth/4) - 20, 20, 80, WHITE);

        EndDrawing();

    }

    CloseWindow();
    return 0;
}