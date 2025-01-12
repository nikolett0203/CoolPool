#include "phylib.h"

/* PART I: CONSTRUCTORS */

/*
 * This constructor allocates memory for a new still ball and initialises its number and position.
 * PARAMETERS: unsigned char (ball's number), phylib_coord (ball's position on the table)
 * RETURN: phylib_object pointer to new still ball
 */

phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos){

    if (pos == NULL) {
        fprintf(stderr, "Error: NULL pointer passed to phylib_new_hole. \n");
        return NULL;
    }

    phylib_object *newStillBall = (phylib_object *)malloc(sizeof(phylib_object));

    if (newStillBall == NULL){
        fprintf(stderr, "Memory allocation failed for phylib_new_still_ball. \n");
        return NULL;
    }

    newStillBall->type = PHYLIB_STILL_BALL;
    newStillBall->obj.still_ball.number = number;
    newStillBall->obj.still_ball.pos = *pos;          

    return newStillBall;

}

/*
 * This constructor allocates memory for a new rolling ball and initialises its number, position, velocity, and acceleration
 * PARAMETERS: unsigned char (ball's number), three phylib_coord pointers (ball's position, velocity, and acceleration, respectively)
 * RETURN: phylib_object pointer to new rolling ball
 */

phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc){

    if (pos == NULL || vel == NULL || acc == NULL) {
        fprintf(stderr, "Error: NULL pointer passed to phylib_new_hole. \n");
        return NULL;
    }

    phylib_object *newRollBall = (phylib_object *)malloc(sizeof(phylib_object));

    if(newRollBall == NULL){
        fprintf(stderr, "Memory allocation failed for phylib_new_rolling_ball. \n");
        return NULL;
    }

    newRollBall->type = PHYLIB_ROLLING_BALL;
    newRollBall->obj.rolling_ball.number = number;
    newRollBall->obj.rolling_ball.pos = *pos;
    newRollBall->obj.rolling_ball.vel = *vel;
    newRollBall->obj.rolling_ball.acc = *acc;

    return newRollBall;

}

/*
 * This constructor allocates memory for a new hole and initialises its position on the table
 * PARAMETERS: phylib_coord pointer (hole's position coordinates)
 * RETURN: phylib_object pointer to new hole
 */

phylib_object *phylib_new_hole(phylib_coord *pos){

    if (pos == NULL) {
        fprintf(stderr, "Error: NULL pointer passed to phylib_new_hole. \n");
        return NULL;
    }

    phylib_object *newHole = (phylib_object *)malloc(sizeof(phylib_object));

    if (newHole == NULL){
        fprintf(stderr, "Memory allocation failed for phylib_new_hole. \n");
        return NULL;
    }

    newHole->type = PHYLIB_HOLE;

    phylib_hole *accessHole = &newHole->obj.hole;

    accessHole->pos = *pos;

    return newHole;

}

/*
 * This constructor allocates memory for a new horizontal cushion and initialises its position on the table
 * PARAMETERS: double (cushion's placement along the y-axis of the table)
 * RETURN: phylib_object pointer to new horizontal cushion
 */

phylib_object *phylib_new_hcushion(double y){

    phylib_object *newHCush = (phylib_object *)malloc(sizeof(phylib_object));

    if (newHCush == NULL){
        fprintf(stderr, "Memory allocation failed for phylib_new_hcushion. \n");
        return NULL;
    }

    newHCush->type = PHYLIB_HCUSHION;
    newHCush->obj.hcushion.y = y;

    return newHCush;

}

/*
 * This constructor allocates memory for a new vertical cushion and initialises its position on the table
 * PARAMETERS: double (cushion's placement along the x-axis of the table)
 * RETURN: phylib_object pointer to new vertical cushion
 */

phylib_object *phylib_new_vcushion(double x){

    phylib_object *newVCush = (phylib_object *)malloc(sizeof(phylib_object));

    if (newVCush == NULL){
        fprintf(stderr, "Memory allocation failed for phylib_new_vcushion. \n");
        return NULL;        
    }

    newVCush->type = PHYLIB_VCUSHION;
    newVCush->obj.vcushion.x = x;

    return newVCush;
}

/*
 * This constructor allocates memory for a new table and initialises an array of the objects on the table,
 * particularly its cushions and holes
 * PARAMETERS: none
 * RETURN: phylib_table pointer to new table
 */

phylib_table *phylib_new_table(void){

    // array of hole positions to avoid having to declare phylib_coord variables six times
    phylib_coord holePos[6] = {
        {0.0, 0.0},  
        {0.0, PHYLIB_TABLE_LENGTH/2}, 
        {0.0, PHYLIB_TABLE_LENGTH},
        {PHYLIB_TABLE_WIDTH, 0.0},
        {PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH/2},                    
        {PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH}
    };

    phylib_table *newTable = (phylib_table *)malloc(sizeof(phylib_table));

    if (newTable == NULL){
        fprintf(stderr, "Memory allocation failed for phylib_new_newtable. \n");
        return NULL;
    }

    newTable->time = 0.0;

    // adding cushions to the table in order
    newTable->object[0] = phylib_new_hcushion(0.0);
    newTable->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);
    newTable->object[2] = phylib_new_vcushion(0.0);
    newTable->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);

    // adding holes to the table (order is from top left to bottom left, then top to bottom right)
    for (int i=0; i<6; i++){
        newTable->object[i+4] = phylib_new_hole(&holePos[i]);
    }


    // check if any allocations failed
    for (int i=0; i<10; i++){
        if (newTable->object[i] == NULL){
            fprintf(stderr, "Memory allocation failed for table object #%d. \n", i);
            return NULL;            
        }
    }

    // set ball indices to null for now
    for (int i=10; i<PHYLIB_MAX_OBJECTS; i++){
        newTable->object[i] = NULL;
    }

    return newTable;

}

/*PART II FUNCTIONS*/

/*
 * This function creates a copy of a phylib_object at a new memory location
 * PARAMETERS: double pointer to phylib_object source, double pointer to phylib_object destination
 * RETURN: void
 */

void phylib_copy_object( phylib_object **dest, phylib_object **src ){

    if(*src != NULL){
        *dest = (phylib_object *)malloc(sizeof(phylib_object));
        memcpy(*dest, *src, sizeof(phylib_object));
    } else{
        *dest = NULL;
    }

}

/*
 * This function creates a copy of a phylib_table and all its objects at a new memory location
 * PARAMETERS: pointer to phylib_table to be copied
 * RETURN: pointer to copy of phylib_table
 */

phylib_table *phylib_copy_table( phylib_table *table ){


    if(table == NULL){
        fprintf(stderr, "Error: table not passed as argument to phylib_copy_table. \n");
        return NULL;
    }

    phylib_table *newTable = (phylib_table *)malloc(sizeof(phylib_table));

    if (newTable == NULL){
        fprintf(stderr, "Memory allocation failed for table. \n");
        return NULL;       
    }

    newTable->time = table->time;

    // copy objects to new table, including any null objects
    for(int i=0; i<PHYLIB_MAX_OBJECTS; i++){
        if(table->object[i] == NULL){
            newTable->object[i] = NULL;
        }else{
            phylib_copy_object(&newTable->object[i], &table->object[i]);            
        }
    }

    return newTable;

}

/*
 * This function searches for a null pointer in the table object array, then adds an object to the array at that location
 * PARAMETERS: pointer to phylib_table, pointer to phylib_object to be added
 * RETURN: void
 */

void phylib_add_object( phylib_table *table, phylib_object *object ){

    if (table == NULL){
        fprintf(stderr, "Error: table not passed as argument to phylib_add_object. \n");
        return;
    }

    for(int i=0; i<PHYLIB_MAX_OBJECTS; i++){
        if (table->object[i] == NULL){
            table->object[i] = object;
            break;
        }
    }

}

/*
 * This function frees the memory of all objects on the table and then frees the table memory
 * PARAMETERS: pointer to phylib_table
 * RETURN: void
 */

void phylib_free_table( phylib_table *table ){

    if(table == NULL){
        fprintf(stderr, "Nothing to free! \n");
        return;
    }

    for(int i=0; i<PHYLIB_MAX_OBJECTS; i++){
        if (table->object[i] != NULL){
            free(table->object[i]);
        }
    }

    free(table);

}

/*
 * This function calculates the difference between two sets of coordinates
 * PARAMETERS: two phylib_coord structs, each containing an (x,y) value pair
 * RETURN: phylib_coord containing the calculated difference 
 */

phylib_coord phylib_sub( phylib_coord c1, phylib_coord c2 ){

    phylib_coord c3;

    c3.x = c1.x - c2.x;
    c3.y = c1.y - c2.y;

    return c3;

}

/*
 * This function calculates the length of the vector parameter using Pythagorean theorem
 * PARAMETERS: phylib_coord containing the vector data
 * RETURN: double representing the vector length
 */

double phylib_length( phylib_coord c ){
    
    return sqrt(c.x*c.x + c.y*c.y); 

}

/*
 * This function computes the dot product between two vectors
 * PARAMETERS: two phylib_coord structs containing vector data
 * RETURN: double representing the dot product
 */

double phylib_dot_product( phylib_coord a, phylib_coord b ){

    return a.x*b.x + a.y*b.y;

}

/*
 * This function computes the distance between two objects on the table
 * PARAMETERS: two phylib_object pointers to table objects
 * RETURN: double representing the distance between the objects
 */

double phylib_distance( phylib_object *obj1, phylib_object *obj2 ){

    phylib_coord difference;
    double distance;

    if (obj1 == NULL || obj2 == NULL || obj1->type != PHYLIB_ROLLING_BALL){
        return -1.0;
    }
    
    // distance calculation varies depending on what object the rolling ball collided with
    switch(obj2->type){
        case PHYLIB_STILL_BALL:
            difference = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.still_ball.pos);
            distance = phylib_length(difference) - PHYLIB_BALL_DIAMETER;
            break;        
        case PHYLIB_ROLLING_BALL:
            difference = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.rolling_ball.pos);
            distance = phylib_length(difference) - PHYLIB_BALL_DIAMETER;
            break;
        case PHYLIB_HOLE:    
            difference = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.hole.pos);  
            distance = phylib_length(difference) - PHYLIB_HOLE_RADIUS;         
            break;
        case PHYLIB_HCUSHION:   
            distance = fabs(obj1->obj.rolling_ball.pos.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;
            break;
        case PHYLIB_VCUSHION:  
            distance = fabs(obj1->obj.rolling_ball.pos.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
            break;
        default:
            distance = -1.0;
            break;
    }
    
    return distance;

}

/*PART III*/

/*
 * This function updates the values of a rolling ball after it has rolled for a period of time
 * PARAMETERS: two phylib_object pointers to an old rolling ball (pre-roll) and a new rolling ball (post-roll), as well as a double for the time
 * RETURN: void
 */

void phylib_roll( phylib_object *new, phylib_object *old, double time ){

    if(new->type != PHYLIB_ROLLING_BALL || old->type != PHYLIB_ROLLING_BALL || new == NULL || old == NULL){
        fprintf(stderr, "Error: NULL or not rolling ball. \n");
        return;
    }

    // update the position of the ball based on the starting point of the old ball
    new->obj.rolling_ball.pos.x = new_position (old->obj.rolling_ball.pos.x, old->obj.rolling_ball.vel.x, old->obj.rolling_ball.acc.x, time);
    new->obj.rolling_ball.pos.y = new_position (old->obj.rolling_ball.pos.y, old->obj.rolling_ball.vel.y, old->obj.rolling_ball.acc.y, time);    

    // for both x and y dimensions of the velocity, if it changes sign, must set velocity and acceleration to zero
    new->obj.rolling_ball.vel.x = new_velocity (old->obj.rolling_ball.vel.x, old->obj.rolling_ball.acc.x, time);
    if (new->obj.rolling_ball.vel.x * old->obj.rolling_ball.vel.x < 0){
        new->obj.rolling_ball.vel.x = 0;
        new->obj.rolling_ball.acc.x = 0;
    }

    new->obj.rolling_ball.vel.y = new_velocity (old->obj.rolling_ball.vel.y, old->obj.rolling_ball.acc.y, time);
    if (new->obj.rolling_ball.vel.y * old->obj.rolling_ball.vel.y < 0){
        new->obj.rolling_ball.vel.y = 0;
        new->obj.rolling_ball.acc.y = 0;
    }

}

/*
 * This function transforms a rolling ball into a still ball if it has stopped rolling
 * PARAMETERS: phylib_object pointer to a rolling ball
 * RETURN: 0 (if the ball has not stopped rolling) or 1 (if the ball is no longer rolling and has been transformed)
 */

unsigned char phylib_stopped( phylib_object *object ){

    if (object == NULL || object->type != PHYLIB_ROLLING_BALL){
        fprintf(stderr, "Error: NULL or not rolling ball. \n");
        return 0;       
    }

    double speed = phylib_length(object->obj.rolling_ball.vel);

    // if ball is still rolling, keep phylib_object as rolling ball
    if (speed >= PHYLIB_VEL_EPSILON){
        return 0;
    }

    // else, update phylib_object to still_ball and transfer values over    
    double tempNum = object->obj.rolling_ball.number;
    phylib_coord tempPos = object->obj.rolling_ball.pos;

    object->type = PHYLIB_STILL_BALL;
    object->obj.still_ball.number = tempNum;
    object->obj.still_ball.pos = tempPos;

    return 1;

}

/*
 * This function executes collisions between a rolling ball and one of: a cushion, a hole, or another ball
 * PARAMETERS: double pointer to 
 * RETURN: void
 */

void phylib_bounce( phylib_object **a, phylib_object **b ){

    if (*a == NULL || *b == NULL){
        fprintf(stderr, "Error: NULL pointers. \n");
        return;        
    }

    if ((*a)->type != PHYLIB_ROLLING_BALL){
        fprintf(stderr, "Error: not rolling ball. \n");      
        return;    
    }

    // objects react differently to collisions so each case calculates the state of the object differently
    switch((*b)->type){
        case PHYLIB_STILL_BALL:
            phylib_goed(b);
        case PHYLIB_ROLLING_BALL:
            ball_to_ball_bounce_calcs(a, b);
            break;
        case PHYLIB_HOLE:
            free(*a);
            *a = NULL;
            break;
        case PHYLIB_HCUSHION:
            (*a)->obj.rolling_ball.vel.y *= -1;
            (*a)->obj.rolling_ball.acc.y *= -1;
            break;
        case PHYLIB_VCUSHION:
            (*a)->obj.rolling_ball.vel.x *= -1;
            (*a)->obj.rolling_ball.acc.x *= -1;
            break;
    }

}

/*
 * This function returns the number of currently rolling balls on the table
 * PARAMETERS: phylib_table pointer
 * RETURN: unsigned char representing the number of rolling balls
 */

unsigned char phylib_rolling( phylib_table *t ){

    unsigned char count = 0;

    if (t == NULL){
        return 0;
    }

    for(int i = 0; i<PHYLIB_MAX_OBJECTS; i++){
        if (t->object[i] == NULL){
            continue;
        }
        else if (t->object[i]->type == PHYLIB_ROLLING_BALL){
            count++;
        }
    }

    return count;

}


phylib_table *phylib_segment( phylib_table *table ){

    if(table == NULL){
        fprintf(stderr, "No table passed\n");
        return NULL;
    }

    // if no balls are rolling, state of the table is the same
    unsigned char result = balls_rolling(table);
    if (result == 0){
        return NULL;
    }

    // create a copy of the table to represent the state after the pool shot
    phylib_table *newTable = phylib_copy_table(table);

    for (double t=PHYLIB_SIM_RATE; t<PHYLIB_MAX_TIME; t+=PHYLIB_SIM_RATE){

        newTable->time += PHYLIB_SIM_RATE;
        
        // for each ball, calculate the change in position over time
        for(int i=10; i<PHYLIB_MAX_OBJECTS; i++){
        
            if(table->object[i] != NULL && table->object[i]->type == PHYLIB_ROLLING_BALL){
                phylib_roll(newTable->object[i], table->object[i], t); 
            }
        
        }

                // compare each ball to every other object on the table to detect collisions
        for (int j=10; j<PHYLIB_MAX_OBJECTS; j++){

            if(newTable->object[j] != NULL && newTable->object[j]->type == PHYLIB_ROLLING_BALL){
                if(phylib_stopped(newTable->object[j])){
                    return newTable; 
                }
            }
            for(int k=0; k<PHYLIB_MAX_OBJECTS; k++){
                if (j!=k && newTable->object[k] != NULL){
                    double distance = phylib_distance(newTable->object[j], newTable->object[k]);
                    if (distance != -1.0 && distance < 0){
                        phylib_bounce(&newTable->object[j], &newTable->object[k]);
                        return newTable; 
                    }
                }
            }
        }
    }
    return newTable;
}


/*HELPER FUNCTIONS*/

/*
 * This function computes the new position of an object in one dimension (either x or y)
 * PARAMETERS: four doubles representing the original position (p1), velocity (v1), acceleration (a1), and time (t)
 * RETURN: double representing the new position
 */

double new_position (double p1, double v1, double a1, double t){
    
    return p1 + v1*t + 0.5*a1*(t*t);

}

/*
 * This function computes the new velocity of an object in one dimension (either x or y)
 * PARAMETERS: three doubles representing the original velocity (v1), acceleration (a1), and time (t)
 * RETURN: double representing the new velocity
 */

double new_velocity (double v1, double a1, double t){
    
    return v1 + a1*t;

}

/*
 * This function converts a still ball into a rolling ball, setting a default velocity and acceleration of 0.0
 * PARAMETERS: double phylib_object pointer representing a still ball
 * RETURN: void
 */

void phylib_goed( phylib_object **object ){

    if (*object == NULL ||(*object)->type != PHYLIB_STILL_BALL){
        fprintf(stderr, "Error: NULL or not still ball. \n");
        return;       
    }
    
    double tempNum = (*object)->obj.still_ball.number;
    phylib_coord tempPos = (*object)->obj.still_ball.pos;
    
    // set default values for velocity and acceleration of new rolling ball
    phylib_coord zero = {0.0, 0.0};

    (*object)->type = PHYLIB_ROLLING_BALL;
    (*object)->obj.rolling_ball.number = tempNum;
    (*object)->obj.rolling_ball.pos = tempPos;
    (*object)->obj.rolling_ball.acc = zero;
    (*object)->obj.rolling_ball.vel = zero;

}

/*
 * This function performs various calculations to update the position, velocity, and acceleration of two collided balls
 * PARAMETERS: two double phylib_object pointer representing the collided balls
 * RETURN: void
 */

void ball_to_ball_bounce_calcs ( phylib_object **a, phylib_object **b ){

    phylib_coord r_ab, v_rel, n;
    double length_rab, v_rel_n, speed_a, speed_b;

    r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);
    v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);
    
    // DIVIDE BY ZERO?
    length_rab = phylib_length(r_ab);
    n.x = r_ab.x/length_rab;
    n.y = r_ab.y/length_rab;

    v_rel_n = phylib_dot_product(n, v_rel);

    (*a)->obj.rolling_ball.vel.x -= (v_rel_n*n.x); 
    (*a)->obj.rolling_ball.vel.y -= (v_rel_n*n.y); 

    (*b)->obj.rolling_ball.vel.x += (v_rel_n*n.x); 
    (*b)->obj.rolling_ball.vel.y += (v_rel_n*n.y); 

    speed_a = phylib_length((*a)->obj.rolling_ball.vel);
    speed_b = phylib_length((*b)->obj.rolling_ball.vel);

    if (speed_a > PHYLIB_VEL_EPSILON){
        (*a)->obj.rolling_ball.acc.x = (-1*(*a)->obj.rolling_ball.vel.x/speed_a)*PHYLIB_DRAG;
        (*a)->obj.rolling_ball.acc.y = (-1*(*a)->obj.rolling_ball.vel.y/speed_a)*PHYLIB_DRAG;
    }

    if(speed_b > PHYLIB_VEL_EPSILON){
        (*b)->obj.rolling_ball.acc.x = (-1*(*b)->obj.rolling_ball.vel.x/speed_b)*PHYLIB_DRAG;
        (*b)->obj.rolling_ball.acc.y = (-1*(*b)->obj.rolling_ball.vel.y/speed_b)*PHYLIB_DRAG;
    }
}

int balls_rolling (phylib_table * table){
    for (int i=0; i<PHYLIB_MAX_OBJECTS; i++){
        if (table->object[i] != NULL && table->object[i]->type == PHYLIB_ROLLING_BALL){
            return 1;
        }
    }
    return 0;
}

/*Random new function*/


char *phylib_object_string( phylib_object *object ){

    static char string[80];

    if (object==NULL){
        snprintf( string, 80, "NULL;" );
        return string;
    }

    switch (object->type){
        case PHYLIB_STILL_BALL:
            snprintf(string, 80,
                    "STILL_BALL (%d,%6.1lf,%6.1lf)",
                    object->obj.still_ball.number,
                    object->obj.still_ball.pos.x,
                    object->obj.still_ball.pos.y);
            break;
        case PHYLIB_ROLLING_BALL:
            snprintf(string, 80,
                    "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
                    object->obj.rolling_ball.number,
                    object->obj.rolling_ball.pos.x,
                    object->obj.rolling_ball.pos.y,
                    object->obj.rolling_ball.vel.x,
                    object->obj.rolling_ball.vel.y,
                    object->obj.rolling_ball.acc.x,
                    object->obj.rolling_ball.acc.y);
            break;
        case PHYLIB_HOLE:
            snprintf(string, 80,
                    "HOLE (%6.1lf,%6.1lf)",
                    object->obj.hole.pos.x,
                    object->obj.hole.pos.y);
                    break;
        case PHYLIB_HCUSHION:
            snprintf(string, 80,
                    "HCUSHION (%6.1lf)",
                    object->obj.hcushion.y);
            break;
        case PHYLIB_VCUSHION:
            snprintf(string, 80,
                    "VCUSHION (%6.1lf)",
                    object->obj.vcushion.x);
            break;
        }

        return string;

    }
