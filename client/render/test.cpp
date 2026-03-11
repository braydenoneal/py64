// https://www.peroxide.dk/papers/collision/collision.pdf
class PLANE {
public:
    float equation[4];
    VECTOR origin;
    VECTOR normal;
    PLANE(const VECTOR& origin, const VECTOR& normal);
    PLANE(const VECTOR& p1, const VECTOR& p2, const VECTOR& p3);
    bool isFrontFacingTo(const VECTOR& direction) const;
    double signedDistanceTo(const VECTOR& point) const;
};

PLANE::PLANE(const VECTOR& origin, const VECTOR& normal) {
    this->normal = normal;
    this->origin = origin;
    equation[0] = normal.x;
    equation[1] = normal.y;
    equation[2] = normal.z;
    equation[3] = -(normal.x*origin.x+normal.y*origin.y+normal.z*origin.z);
}

// Construct from triangle:
PLANE::PLANE(const VECTOR& p1,const VECTOR& p2,const VECTOR& p3) {
    normal = (p2-p1).cross(p3-p1);
    normal.normalize();
    origin = p1;
    equation[0] = normal.x;
    equation[1] = normal.y;
    equation[2] = normal.z;
    equation[3] = -(normal.x*origin.x+normal.y*origin.y+normal.z*origin.z);
}

bool PLANE::isFrontFacingTo(const VECTOR& direction) const {
    double dot = normal.dot(direction);
    return (dot <= 0);
}

double PLANE::signedDistanceTo(const VECTOR& point) const {
    //
    return (point.dot(normal)) + equation[3];
}

class CollisionPacket {
public:
    VECTOR eRadius; // ellipsoid radius
    // Information about the move being requested: (in R3)
    VECTOR R3Velocity;
    VECTOR R3Position;
    // Information about the move being requested: (in eSpace)
    VECTOR velocity;
    VECTOR normalizedVelocity;
    VECTOR basePoint;
    // Hit information
    bool foundCollision;
    double nearestDistance;
    VECTOR intersectionPoint;
};

// Assumes: p1,p2 and p3 are given in ellipsoid space:
void checkTriangle(CollisionPacket* colPackage, const VECTOR& p1,const VECTOR& p2,const VECTOR& p3) {
    // Make the plane containing this triangle.
    PLANE trianglePlane(p1,p2,p3);
    // Is triangle front-facing to the velocity vector?
    // We only check front-facing triangles
    // (your choice of course)
    if (trianglePlane.isFrontFacingTo(colPackage->normalizedVelocity)) {
        // Get interval of plane intersection:
        double t0, t1;
        bool embeddedInPlane = false;
        // Calculate the signed distance from sphere
        // position to triangle plane
        double signedDistToTrianglePlane = trianglePlane.signedDistanceTo(colPackage->basePoint);
        // cache this as we’re going to use it a few times below:
        float normalDotVelocity = trianglePlane.normal.dot(colPackage->velocity);
        // if sphere is travelling parallel to the plane:
        if (normalDotVelocity == 0.0f) {
            if (fabs(signedDistToTrianglePlane) >= 1.0f) {
                // Sphere is not embedded in plane.
                // No collision possible:
                return;
            }
            else {
                // sphere is embedded in plane.
                // It intersects in the whole range [0..1]
                embeddedInPlane = true;
                t0 = 0.0;
                t1 = 1.0;
            }
        }
        else {
            // N dot D is not 0. Calculate intersection interval:
            t0=(-1.0-signedDistToTrianglePlane)/normalDotVelocity;
            t1=( 1.0-signedDistToTrianglePlane)/normalDotVelocity;
            // Swap so t0 < t1
            if (t0 > t1) {
                double temp = t1;
                t1 = t0;
                t0 = temp;
            }
            // Check that at least one result is within range:
            if (t0 > 1.0f || t1 < 0.0f) {
                // Both t values are outside values [0,1]
                // No collision possible:
                return;
            }
            // Clamp to [0,1]
            if (t0 < 0.0) t0 = 0.0;
            if (t1 < 0.0) t1 = 0.0;
            if (t0 > 1.0) t0 = 1.0;
            if (t1 > 1.0) t1 = 1.0;
        }
        // OK, at this point we have two time values t0 and t1
        // between which the swept sphere intersects with the
        // triangle plane. If any collision is to occur it must
        // happen within this interval.
        VECTOR collisionPoint;
        bool foundCollision = false;
        float t = 1.0;
        // First we check for the easy case - collision inside
        // the triangle. If this happens it must be at time t0
        // as this is when the sphere rests on the front side
        // of the triangle plane. Note, this can only happen if
        // the sphere is not embedded in the triangle plane.
        if (!embeddedInPlane) {
            VECTOR planeIntersectionPoint = (colPackage->basePoint-trianglePlane.normal) + t0*colPackage->velocity;
            if (checkPointInTriangle(planeIntersectionPoint,p1,p2,p3)) {
                foundCollision = true;
                t = t0;
                collisionPoint = planeIntersectionPoint;
            }
        }
        // if we haven’t found a collision already we’ll have to
        // sweep sphere against points and edges of the triangle.
        // Note: A collision inside the triangle (the check above)
        // will always happen before a vertex or edge collision!
        // This is why we can skip the swept test if the above
        // gives a collision!
        if (foundCollision == false) {
            // some commonly used terms:
            VECTOR velocity = colPackage->velocity;
            VECTOR base = colPackage->basePoint;
            float velocitySquaredLength = velocity.squaredLength();
            float a,b,c; // Params for equation
            float newT;
            // For each vertex or edge a quadratic equation have to
            // be solved. We parameterize this equation as
            // a*t^2 + b*t + c = 0 and below we calculate the
            // parameters a,b and c for each test.
            // Check against points:
            a = velocitySquaredLength;
            // P1
            b = 2.0*(velocity.dot(base-p1));
            c = (p1-base).squaredLength() - 1.0;
            if (getLowestRoot(a,b,c, t, &newT)) {
                t = newT;
                40
                foundCollision = true;
                collisionPoint = p1;
            }
            // P2
            b = 2.0*(velocity.dot(base-p2));
            c = (p2-base).squaredLength() - 1.0;
            if (getLowestRoot(a,b,c, t, &newT)) {
                t = newT;
                foundCollision = true;
                collisionPoint = p2;
            }
            // P3
            b = 2.0*(velocity.dot(base-p3));
            c = (p3-base).squaredLength() - 1.0;
            if (getLowestRoot(a,b,c, t, &newT)) {
                t = newT;
                foundCollision = true;
                collisionPoint = p3;
            }
            // Check against edges:
            // p1 -> p2:
            VECTOR edge = p2-p1;
            VECTOR baseToVertex = p1 - base;
            float edgeSquaredLength = edge.squaredLength();
            float edgeDotVelocity = edge.dot(velocity);
            float edgeDotBaseToVertex = edge.dot(baseToVertex);
            // Calculate parameters for equation
            a = edgeSquaredLength*-velocitySquaredLength + edgeDotVelocity*edgeDotVelocity;
            b = edgeSquaredLength*(2*velocity.dot(baseToVertex))- 2.0*edgeDotVelocity*edgeDotBaseToVertex;
            c = edgeSquaredLength*(1-baseToVertex.squaredLength())+ edgeDotBaseToVertex*edgeDotBaseToVertex;
            // Does the swept sphere collide against infinite edge?
            if (getLowestRoot(a,b,c, t, &newT)) {
                // Check if intersection is within line segment:
                float f=(edgeDotVelocity*newT-edgeDotBaseToVertex)/
                edgeSquaredLength;
                if (f >= 0.0 && f <= 1.0) {
                    // intersection took place within segment.
                    t = newT;
                    foundCollision = true;
                    collisionPoint = p1 + f*edge;
                }
            }
            // p2 -> p3:
            edge = p3-p2;
            baseToVertex = p2 - base;
            edgeSquaredLength = edge.squaredLength();
            edgeDotVelocity = edge.dot(velocity);
            edgeDotBaseToVertex = edge.dot(baseToVertex);
            a = edgeSquaredLength*-velocitySquaredLength +
            edgeDotVelocity*edgeDotVelocity;
            b = edgeSquaredLength*(2*velocity.dot(baseToVertex))-2.0*edgeDotVelocity*edgeDotBaseToVertex;
            c = edgeSquaredLength*(1-baseToVertex.squaredLength())+edgeDotBaseToVertex*edgeDotBaseToVertex;
            if (getLowestRoot(a,b,c, t, &newT)) {
                float f=(edgeDotVelocity*newT-edgeDotBaseToVertex)/
                edgeSquaredLength;
                if (f >= 0.0 && f <= 1.0) {
                    t = newT;
                    foundCollision = true;
                    collisionPoint = p2 + f*edge;
                }
            }
            // p3 -> p1:
            edge = p1-p3;
            baseToVertex = p3 - base;
            edgeSquaredLength = edge.squaredLength();
            edgeDotVelocity = edge.dot(velocity);
            edgeDotBaseToVertex = edge.dot(baseToVertex);
            a = edgeSquaredLength*-velocitySquaredLength +edgeDotVelocity*edgeDotVelocity;
            b = edgeSquaredLength*(2*velocity.dot(baseToVertex))-2.0*edgeDotVelocity*edgeDotBaseToVertex;
            c = edgeSquaredLength*(1-baseToVertex.squaredLength())+edgeDotBaseToVertex*edgeDotBaseToVertex;
            if (getLowestRoot(a,b,c, t, &newT)) {
                float f=(edgeDotVelocity*newT-edgeDotBaseToVertex)/
                edgeSquaredLength;
                if (f >= 0.0 && f <= 1.0) {
                    t = newT;
                    foundCollision = true;
                    collisionPoint = p3 + f*edge;
                }
            }
        }
        // Set result:
        if (foundCollision == true) {
            // distance to collision: ’t’ is time of collision
            float distToCollision = t*colPackage->velocity.length();
            // Does this triangle qualify for the closest hit?
            // it does if it’s the first hit or the closest
            if (colPackage->foundCollision == false ||
            distToCollision < colPackage->nearestDistance) {
                // Collision information necessary for sliding
                colPackage->nearestDistance = distToCollision;
                colPackage->intersectionPoint=collisionPoint;
                colPackage->foundCollision = true;
            }
        }
    } // if not backface
}

void CharacterEntity::collideAndSlide(const VECTOR& vel,const VECTOR& gravity) {
    // Do collision detection:
    collisionPackage->R3Position = position;
    collisionPackage->R3Velocity = vel;
    // calculate position and velocity in eSpace
    VECTOR eSpacePosition = collisionPackage->R3Position/collisionPackage->eRadius;
    VECTOR eSpaceVelocity = collisionPackage->R3Velocity/collisionPackage->eRadius;
    // Iterate until we have our final position.
    collisionRecursionDepth = 0;
    VECTOR finalPosition = collideWithWorld(eSpacePosition,eSpaceVelocity);
    // Add gravity pull:
    // To remove gravity uncomment from here .....
    // Set the new R3 position (convert back from eSpace to R3
    collisionPackage->R3Position = finalPosition*collisionPackage->eRadius;
    collisionPackage->R3Velocity = gravity;
    eSpaceVelocity = gravity/collisionPackage->eRadius;
    collisionRecursionDepth = 0;
    finalPosition = collideWithWorld(finalPosition,eSpaceVelocity);
    // ... to here
    // Convert final result back to R3:
    finalPosition = finalPosition*collisionPackage->eRadius;
    // Move the entity (application specific function)
    MoveTo(finalPosition);
}

// Set this to match application scale..
const float unitsPerMeter = 100.0f;
VECTOR CharacterEntity::collideWithWorld(const VECTOR& pos,const VECTOR& vel) {
    // All hard-coded distances in this function is
    // scaled to fit the setting above..
    float unitScale = unitsPerMeter / 100.0f;
    float veryCloseDistance = 0.005f * unitScale;
    // do we need to worry?
    if (collisionRecursionDepth>5)
        return pos;
    // Ok, we need to worry:
    collisionPackage->velocity = vel;
    collisionPackage->normalizedVelocity = vel;
    collisionPackage->normalizedVelocity.normalize();
    collisionPackage->basePoint = pos;
    collisionPackage->foundCollision = false;
    // Check for collision (calls the collision routines)
    // Application specific!!
    world->checkCollision(collisionPackage);
    // If no collision we just move along the velocity
    if (collisionPackage->foundCollision == false) {
        return pos + vel;
    }
    // *** Collision occurred ***
    // The original destination point
    VECTOR destinationPoint = pos + vel;
    VECTOR newBasePoint = pos;
    // only update if we are not already very close
    // and if so we only move very close to intersection..not
    // to the exact spot.
    if (collisionPackage->nearestDistance>=veryCloseDistance) {
        VECTOR V = vel;
        V.SetLength(collisionPackage->nearestDistance-veryCloseDistance);
        newBasePoint = collisionPackage->basePoint + V;
        // Adjust polygon intersection point (so sliding
        // plane will be unaffected by the fact that we
        // move slightly less than collision tells us)
        V.normalize();
        collisionPackage->intersectionPoint -=
        veryCloseDistance * V;
    }
    // Determine the sliding plane
    VECTOR slidePlaneOrigin = collisionPackage->intersectionPoint;
    VECTOR slidePlaneNormal = newBasePoint-collisionPackage->intersectionPoint;
    slidePlaneNormal.normalize();
    PLANE slidingPlane(slidePlaneOrigin,slidePlaneNormal);
    // Again, sorry about formatting.. but look carefully ;)
    VECTOR newDestinationPoint = destinationPoint -
    slidingPlane.signedDistanceTo(destinationPoint)*
    slidePlaneNormal;
    // Generate the slide vector, which will become our new
    // velocity vector for the next iteration
    VECTOR newVelocityVector = newDestinationPoint -
    collisionPackage->intersectionPoint;
    // Recurse:
    // dont recurse if the new velocity is very small
    if (newVelocityVector.length() < veryCloseDistance) {
        return newBasePoint;
    }
    collisionRecursionDepth++;
    return collideWithWorld(newBasePoint,newVelocityVector);
}
