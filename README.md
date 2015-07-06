# pr_ordata
pr_ordata is a repository of [OpenRAVE](http://openrave.org/) resources used by
the [Personal Robotics Lab](https://personalrobotics.ri.cmu.edu/) in the
[Robotics Institute](https://www.ri.cmu.edu/) at [Carnegie Mellon
University](http://www.cmu.edu/). Primarily, this includes a repository of
meshes and [KinBody XML](http://openrave.programmingvision.com/wiki/index.php/Format:XML)
specifications for objects commonly encountered by HERB and ADA.

**Warning:** The models in this package depend on features recently added to
OpenRAVE 0.9. In particular, your version of OpenRAVE must support geometry
groups in the `.kinbody.xml` format added in commit
[b032128](https://github.com/rdiankov/openrave/commit/b0321283fdd65ca7466f89bf7aefc17812267948).

## Loading Models

This package uses the
[openrave_catkin](https://github.com/personalrobotics/openrave_catkin) package
to automatically manage the `OPENRAVE_DATA` environment variable. This means
that, once this package is built using `catkin_make`, you should be able to
import any model in the `data/` directory with a relative path. For example:

    kinbody = env.ReadKinbodyURI('objects/pop_tarts.kinbody.xml')
    env.Add(kinbody)

## Model Creation Guidelines

We currently split models into two categories. Static objects in the
environment (e.g. tables, chairs, shelves) are in the *furniture* directory.
Any objects that can be grasped are in the *objects* directory. You are welcome
to create additional categories if it seems appropriate to do so.

### Naming Convention

We follow this naming convention for models of rigid bodies:

- `model_name.kinbody.xml`: OpenRAVE [KinBody specification](http://openrave.programmingvision.com/wiki/index.php/Format:XML)
- `model_name_collision.stl`: collision geometry (as small as possible)
- `model_name_visual.dae`: visual geometry; medium resolution (< 500 kB)
- `model_name_visual_0.jpg`: textures for visual geometry (< 500 kB)
- `model_name_scan.dae`: raw model produced by the 3D scanner
- `model_name_scan_0.jpg`: raw texture produced by the 3D model

Note that some models (e.g. un-textured objects, primitive collision geometry)
may only require a subset of these files. Additionally, we do not have a strict
naming convention for articulated bodies. Please try your best to stay
consistent with the existing models.

### Sphere Approximation

All *objects* **should define a `spheres` geometry group** that includes a
conservative (i.e.  over-approximation) decomposition of the object's collision
geometry as a collection of one or more spheres. These spheres can be created
in a `.kinbody.xml` file using the following syntax:

    <!-- ... -->
    <Geom type="sphere" group="spheres">
      <Translation>0 0 0</Translation>
      <Radius>0.1</Radius>
    </Geom>
    <!-- ... -->

The approximation is necessary to plan with
[CHOMP](https://github.com/personalrobotics/or_cdchomp) while the object is
grasped. Specifying a non-conservative approximation may cause CHOMP to return
infeasible trajectories.

## Contributors

pr_ordata was developed by the [Personal Robotics Lab](https://personalrobotics.ri.cmu.edu)
in the [Robotics Institute](http://ri.cmu.edu) at [Carnegie Mellon University](http://www.cmu.edu).
The packaging and conventions listed above were developed collaboratively by
[Michael Koval](http://mkoval.org) and [Aaron Walsman](http://www.ri.cmu.edu/person.html?person_id=3158).
