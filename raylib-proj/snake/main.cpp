// GAME STEPS
// 1. DONE Draw board
// 2. Draw snake
// 3. Get snake to move correctly
// 4. Get snake to collide with walls
// 5. Get snake to collide with itself
// 6. Create apples

// PROBLEMS:
// - snake can change direction on a point
// - what order should member functions be
// - change direction and eat fruit in same square

#include <iostream>
#include <raylib.h>
#include <raymath.h>
#include <vector>
#include <cmath>
#include <algorithm>
#include <array>

// constansts and global variables
const int SQUARE_LENGTH = 50;
const int BOARD_WIDTH = 1200;
const int BOARD_HEIGHT = 650;
Color lightGreen{121, 208, 33, 255};
Color darkGreen{55, 174, 15, 255};
Color sheerGrey{96, 96, 96, 100};
bool isGameStarted = true;

// to print vectors
std::ostream& operator<<(std::ostream& os, const Vector2& p) {
    os << "(" << p.x << ", " << p.y << ")";
    return os;
}

// returns true if p is between a and b
bool isBetween(float a, float b, float p) {
    // assuming a > b
    if (p >= b && p <= a) {
        return true;
    } else if(p >= a && p <= b){
        // assuming b > a
        return true;
    }
    return false;
}

// Class definitions
class Snake {
    private:
        Vector2 m_Head;
        Vector2 m_Tail;
        int m_SegmentCount;
        std::vector<Vector2> m_Points;   // stores end of each segment in the snake
        bool turnRight;
        bool turnLeft;
        bool turnUp;
        bool turnDown;

    public:
        Snake(Vector2 h, Vector2 t, std::vector<Vector2> p);
        void UpdateSnake();
        bool eatFruit(Vector2 v);
        void drawSnake();
        void resetSnake();
        bool wallCollision();
        bool snakeCollision(Vector2 v, char d);
        bool selfCollision();
        Vector2 getUnitVector(int a); 
        void changeDirection(Vector2 v);
        void growSnake();
};

class Board {
    private:
        const int m_Width;
        const int m_Height;
    public:
        Board(int w, int h);
        void setHeight(int h);
        void setWidth(int w);
        int getWidth();
        int getHeight();
        void drawBoard();
};

class Fruit {
    private:
        Vector2 m_Location;
        Snake& m_Snake;

    public:
        Fruit(Vector2 l, Snake& s);
        Vector2 getLocation();
        void setLocation();
        void drawFruit();
        bool fruitCollision(Snake s);
};

// Fruit constructor
Fruit::Fruit(Vector2 l, Snake& s) : m_Location(l), m_Snake(s) {
}

// draws Fruit
void Fruit::drawFruit() {
    DrawCircle(m_Location.x, m_Location.y, 20.0, RED);
}

// gets m_Location
Vector2 Fruit::getLocation() {
    return m_Location;
}

// sets random location of fruit
void Fruit::setLocation(){
    
    const int xSquareNum = BOARD_WIDTH/SQUARE_LENGTH;   // number of gameboard squares across
    const int ySqaureNum = BOARD_HEIGHT/SQUARE_LENGTH;  // number of gameboard squares vertically 

    std::array<int, xSquareNum> possibleX;      
    std::array<int, ySqaureNum> possibleY;     

    for(int i=0;i<xSquareNum;i++) {
        possibleX[i] = 75 + (i*SQUARE_LENGTH); 
    }
    for(int i=0;i<ySqaureNum;i++) {
        possibleY[i] = 125 + (i*SQUARE_LENGTH);
    }
    do {    // keep assigning random locations to fruit until fruitCollision == false
        m_Location.x = (possibleX[GetRandomValue(0, possibleX.size()-1)]);
        m_Location.y = (possibleY[GetRandomValue(0, possibleY.size()-1)]);
    } while (fruitCollision(m_Snake));

    std::cout << "New location of fruit: " << m_Location << std::endl;
}

Snake::Snake(Vector2 h, Vector2 t, std::vector<Vector2> p) : m_Head(h), m_Tail(t), m_Points(p) {
    m_SegmentCount = m_Points.size() - 1;  // if a snake has three points--head, middle, tail-- it has two segments
    turnRight = false;
    turnLeft = false;
    turnUp = false;
    turnDown = false;
}

// draws Snake object
void Snake::drawSnake() {
    for (int i=0;i<m_SegmentCount; i++) {
        Vector2 v = getUnitVector(i);
        v = Vector2Scale(v, 15.0);
        DrawLineEx(m_Points[i], (Vector2Subtract(m_Points[i+1], v)), 30.0, BLUE);
    }
}

// returns the unit vector between m_Points[a] and m_Points[a+1] 
// a -> b = (b.x, b.y) - (a.x, a.y)
// head = a, m_Points[second n-1] = a
Vector2 Snake::getUnitVector(int a) {
    Vector2 v = Vector2Subtract(m_Points[a], m_Points[a+1]);
    v = Vector2Normalize(v);
    v = {round(v.x), round(v.y)};

    return v;
}

// changes direction based on given vector v
void Snake::changeDirection(Vector2 v){
    Vector2 newHead = Vector2Add(m_Points[0], v);
    m_SegmentCount++;
    auto it = m_Points.begin();     
    it = m_Points.insert(it, newHead);
    m_Head = m_Points[0];
}

// updates location of snake
void Snake::UpdateSnake() {
    
    // updating m_Head
    m_Points[0] = Vector2Add(m_Points[0], getUnitVector(0));    
    m_Head = m_Points[0];                                    

    // updating m_Tail
    m_Points[m_SegmentCount] = Vector2Add(m_Points[m_SegmentCount], getUnitVector(m_SegmentCount-1));   

    // if segment is gone, ie two segment points are equal
    if(Vector2Equals(m_Points[m_SegmentCount], m_Points[m_SegmentCount-1]) == 1) {
        // last two  points are the same 
        m_Points.pop_back();
        m_SegmentCount = m_Points.size() - 1;  // updating pointCount if points are the same
    }
    m_Tail = m_Points[m_SegmentCount];                         

    // if user changes direction
    if(FloatEquals(getUnitVector(0).x, 0.0f) == 1) { // snake is moving up/down -> current head unit vector = (0, 1) or (0, -1)
        if(IsKeyPressed(KEY_RIGHT)) {
            turnRight = true;
        } else if(IsKeyPressed(KEY_LEFT)) {
            turnLeft = true;
        }
    } else {
        // snake is moving left/right -> current headUnitVector = (1, 0) or (-1, 0)
        if(IsKeyPressed(KEY_DOWN)) {
            turnDown = true;
        } else if(IsKeyPressed(KEY_UP)) {
            turnUp = true;
        }
    }

    // waiting until within square to change direction
    if(int(m_Head.y) % 25 == 0 && (int(m_Head.y) % 10) == 5) {
        if(turnRight) {
            changeDirection({1.0f, 0.0f});
            turnRight = false;
        } else if(turnLeft) {
            changeDirection({-1.0f, 0.0f});
            turnLeft = false;
        }
    } 
    if((int(m_Head.x) % 25) == 0 && (int(m_Head.x) % 10) == 5) {
        if(turnDown) {
            changeDirection({0.0f, 1.0f});
            turnDown = false;
        } else if(turnUp) {
            changeDirection({0.0f, -1.0f});
            turnUp = false;
        }
    }
}

// returns true if m_Head and fruit location are the same and grows snake 
bool Snake::eatFruit(Vector2 v) {
    if(Vector2Equals(m_Head, v) == 1) {
        // grow snake
        Vector2 direction = getUnitVector(m_SegmentCount-1);
        direction = Vector2Negate(direction);
        direction = Vector2Scale(direction, 50.0);
        m_Tail = Vector2Add(direction, m_Tail);
        m_Points[m_SegmentCount] = Vector2Add(direction, m_Points[m_SegmentCount]);

        return true;
    }
    return false;
}

// INC
void Snake::resetSnake() {
    while(isGameStarted == false) {
        DrawRectangle(150, 200, 1000, 450, sheerGrey);
        DrawText("Game over! Enter spacebar to play again.", 200, 350, 60, WHITE);
        if(IsKeyPressed(KEY_SPACE)) {
            isGameStarted = true;
            break;
        }
    }
}

// return true if snake collides with a wall
bool Snake::wallCollision() {
    if(m_Head.x <= 50 || m_Head.x >= 1250 || m_Head.y <= 100 || m_Head.y >= 750) {
        return true;
    } else {
        return false;
    }
}


// returns true if Vector2 v collides with snake body in d direction (pass either x or y)
bool Snake::snakeCollision(Vector2 v, char d) {
    if(d == 'y') {
        // checking for vertical collision
        for(int i=0;i<m_SegmentCount;i++) {
            if(FloatEquals(m_Points[i].y, m_Points[i+1].y) == 1 && FloatEquals(m_Points[i].y, v.y)) {   
                if(isBetween(m_Points[i].x, m_Points[i+1].x, v.x)) {
                    // if two points and m_Head have the same y-pos, and if m_Head.x is between x-pos of the points
                    return true;
                }

            }
        }
    } else if (d == 'x') {
        // checking for hoizontal collision
        for(int i=0;i<m_SegmentCount;i++) {
            if(FloatEquals(m_Points[i].x, m_Points[i+1].x) == 1 && FloatEquals(m_Points[i].x, v.x)) {
                if(isBetween(m_Points[i].y, m_Points[i+1].y, v.y)) {
                    // if two points and m_Head have the same y-pos, and if m_Head.x is between x-pos of the points
                    return true;
                }
            }
        }
    } 

    return false;

}

// returns true if m_Head collides with snake body
bool Snake::selfCollision() {
    if(getUnitVector(0).y != 0) {
        //vertical collision
        return snakeCollision(m_Head, 'y');
    } else if(getUnitVector(0).x != 0) {
        // horizontal collision
        return snakeCollision(m_Head, 'x');
    }
    return false;
}

// check if location collides with body of snake
bool Fruit::fruitCollision(Snake s) {
    if (s.snakeCollision(m_Location, 'x') || s.snakeCollision(m_Location, 'y')) {
        // location of fruit collides with body of snake in either a vertical or horizontal collision
        return true;
    } else {
        return false;
    }
}

// Board constructor
Board::Board(int w, int h) : m_Width(w), m_Height(h) {
}

// draws gameboard 
void Board::drawBoard() {
    bool shiftDown = false;
    DrawRectangle(SQUARE_LENGTH, 100, m_Width, m_Height, lightGreen);
    
    for (int i=SQUARE_LENGTH; i<(m_Width + SQUARE_LENGTH);i += SQUARE_LENGTH){    // x position
        if(shiftDown) {
            for(int j = (100 + SQUARE_LENGTH); j<(m_Height+100); j += (SQUARE_LENGTH*2)) {    // y position
            DrawRectangle(i, j, SQUARE_LENGTH, SQUARE_LENGTH, darkGreen);
            } 
        } else {
            for(int j = 100; j<(m_Height+100); j += (SQUARE_LENGTH*2)) {    // y position
                DrawRectangle(i, j, SQUARE_LENGTH, SQUARE_LENGTH, darkGreen);
            }
        }
        shiftDown = !shiftDown;
    }
    DrawRectangleLines(SQUARE_LENGTH, 100, m_Width, m_Height, BROWN);
}

int Board::getHeight() {
    return m_Height;
}

int Board::getWidth() {
    return m_Width;
}

int main () {
    const int SCREEN_WIDTH = 1300;
    const int SCREEN_HEIGHT = 800;

    int score = 0;

    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Snake Game");
    SetTargetFPS(100); // speed of game, frames per second
    std::vector<Vector2> snakePoints;

    // starting position of the snake 
    snakePoints.push_back({575.0f, 375.0f});                
    snakePoints.push_back({175.0f, 375.0f});

    Snake snake(snakePoints[0], snakePoints[1],  snakePoints);  

    Board gameBoard(BOARD_WIDTH, BOARD_HEIGHT);

    Fruit fruit({975.0f, 375.0f}, snake);

    // game loop
    while(WindowShouldClose() == false) {   // if esc or close icon is pressed
        BeginDrawing();                     // creates a blank canvas

        // draw game objects
        ClearBackground(BLACK);
        gameBoard.drawBoard();
        snake.drawSnake();
        fruit.drawFruit();

        DrawText("Score:", 50, 70, 30, WHITE);
        DrawText(TextFormat("%i", score), 155, 70, 30, WHITE);


        // check for eating fruit
        if(snake.eatFruit(fruit.getLocation())) {
            std::cout << "fruit if\n";
            fruit.setLocation();                // FIX THIS, pass in dimensions of board
            score++;
        }
        // check for collision
        if(snake.wallCollision() || snake.selfCollision()) {
            break;
        }

        // update game objects
        snake.UpdateSnake();
        // std::cout << "snake updated\n";



        EndDrawing();
    }
    CloseWindow();
    return 0;
}
