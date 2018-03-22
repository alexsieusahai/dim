<!DOCTYPE html>
<html lang="en">
  <head>
    <title>A-Frame Examples</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      html {
        font-size: 14px;
      }
      body {
        background: rgb(239,45,94);
        color: #fff;
        font: normal 500 1.2rem/1.2 Inconsolata, Andale Mono, Courier New, monospace;
        padding: 1rem 2rem;
      }
      ul {
        list-style: none;
        margin: 0;
        padding: 0;
      }
      .header {
        position: relative;
      }
      .resources {
        font-size: 0;  /* Collapse whitespace. */
        text-transform: uppercase;
      }
      .resources li + li {
        margin-top: 0.5rem;
      }
      .resources a {
        color: rgba(0,0,0,.5);
        display: inline-block;
        font-size: 1.2rem;
        margin: -0.25rem -0.5rem;
        padding: 0.25rem 0.5rem;
        text-decoration: none;
        transition: all 0.075s ease-in-out;
      }
      .resources a:hover {
        background-color: rgba(0,0,0,0.25);
        color: #fff;
      }
      h1,
      h2 {
        line-height: 100%;
      }
      h1 {
        font-size: 1.6rem;
        font-weight: 100;
        letter-spacing: 0.04rem;
        margin-bottom: 1.25rem;
        text-transform: uppercase;
      }
      h2 {
        color: rgba(0,0,0,0.5);
        font-size: 0.9rem;
        font-weight: 300;
        margin: 2rem 0 0.5rem;
        padding: 0;
        text-transform: uppercase;
      }
      hr {
        background: none;
        border: 0;
        border-bottom: 1px dashed rgba(255,255,255,0.25);
        margin: 2rem 0;
      }
      .links li + li {
        box-shadow: inset 0 0.15rem 0.1rem -0.15rem rgba(0,0,0,0.5);
      }
      .links a {
        color: #fff;
        display: block;
        font-size: 1.5rem;
        letter-spacing: 0.01em;
        padding: 0.75rem 0;
        text-decoration: none;
        transition: opacity 0.075s ease-in-out;
      }
      .links a em {
        font-size: .9rem;
        font-style: normal;
        opacity: .6;
      }
      .links a:hover {
        background-color: rgba(0,0,0,0.15);
        box-shadow: inset 0 0 0 0.15rem rgba(0,0,0,0.15);
      }
      .links a:active {
        background-color: rgba(0,0,0,0.25);
        opacity: 0.75;
      }
      .links li:hover,
      .links li:hover + li {
        margin: 0 -0.75rem;
      }
      .links li:hover a,
      .links li:hover + li a {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
      }
      .moz-link {
        display: block;
        margin: -2.4rem;
        padding: 2rem;
        opacity: 0.5;
        position: absolute;
        top: 0;
        right: 0;
        text-align: right;
        transition: 0.075s opacity ease-in-out;
      }
      .moz-link:hover {
        opacity: 1;
      }
      .moz-logo {
        display: block;
        height: 1.7rem;
      }
      @media only screen and (min-width: 1000px) {
        h1 {
          font-size: 3rem;
        }
        .resources {
          font-size: 1.2;
        }
        .resources li {
          display: inline-block;
        }
        .resources li + li {
          margin-left: 2.5rem;
        }
        .moz-link {
          top: 1.2rem;
          height: 1.8rem;
        }
      }
    </style>
  </head>
  <body>
    <header class="header">
      <h1>A-Frame Examples</h1>
      <a href="https://mozilla.org/" class="moz-link"><img src="assets/img/moz-logo-one-color-white-rgb.svg" class="moz-logo" alt="Mozilla" title="Mozilla"></a>
      <ul id="resources" class="resources">
        <li><a href="https://aframe.io">aframe.io</a></li>
        <li><a href="https://github.com/aframevr">GitHub</a></li>
        <li><a href="https://aframevr-slack.herokuapp.com/">Slack</a></li>
        <li><a href="https://twitter.com/aframevr">Twitter</a></li>
        <li><a href="https://cdn.aframe.io">Asset Uploader</a></li>
      </ul>
    </header>

    <hr>

    <h2>Showcase</h2>

    <ul class="links">
      <li><a href="showcase/anime-UI/">Anime UI</a></li>
      <li><a href="showcase/composite/">Composite</a></li>
      <li><a href="showcase/curved-mockups/">Curved Mockups</a></li>
      <li><a href="showcase/dynamic-lights/">Dynamic Lights</a></li>
      <li><a href="showcase/link-traversal/">Link Traversal</a></li>
      <li><a href="showcase/tracked-controls/">Tracked Controls</a></li>
      <li><a href="showcase/shopping/">Shopping</a></li>
      <li><a href="showcase/spheres-and-fog/">Spheres and Fog</a></li>
      <li><a href="showcase/wikipedia/">Wikipedia</a></li>
    </ul>

    <h2>Boilerplates</h2>

    <ul class="links">
      <li><a href="boilerplate/hello-world/">Hello World</a></li>
      <li><a href="boilerplate/panorama/">360&deg; Image</a></li>
      <li><a href="boilerplate/360-video/">360&deg; Video</a></li>
      <li><a href="boilerplate/3d-model/">3D Model (COLLADA)</a></li>
    </ul>

    <h2>Animations</h2>

    <ul class="links">
      <li><a href="animation/aframe-logo/">A-Frame Logo</a></li>
      <li><a href="animation/arms/">Arms</a></li>
      <li><a href="animation/plane-reveals/">Plane Reveals</a></li>
      <li><a href="animation/generic-logo/">Generic Logo</a></li>
      <li><a href="animation/pivots/">Pivots</a></li>
      <li><a href="animation/unfold/">Unfold</a></li>
      <li><a href="animation/warps/">Warps</a></li>
    </ul>

    <h2>Tests</h2>

    <ul class="links">
      <li><a href="test/animation/">Animation</a></li>
      <li><a href="test/animation-color/">Animation of Color</a></li>
      <li><a href="test/canvas-texture/">Canvas Texture</a></li>
      <li><a href="test/cube/">Cube</a></li>
      <li><a href="test/cursor/">Cursor</a></li>
      <li><a href="test/cylinders/">Cylinders</a></li>
      <li><a href="test/embedded/">Embedded</a></li>
      <li><a href="test/fog/">Fog</a></li>
      <li><a href="test/geometry/">Geometry</a></li>
      <li><a href="test/geometry-gallery/">Geometry Gallery</a></li>
      <li><a href="test/geometry-merging/">Geometry Merging</a></li>
      <li><a href="test/gltf-model/">glTF Model</a></li>
      <li><a href="test/laser-controls/">Laser Controls</a></li>
      <li><a href="test/mixin/">Mixin</a></li>
      <li><a href="test/model/">Model <em>(glTF, OBJ, COLLADA)</em></a></li>
      <li><a href="test/opacity/">Opacity</a></li>
      <li><a href="test/physical/">Physically-Based Materials</a></li>
      <li><a href="test/pivot/">Pivot</a></li>
      <li><a href="primitives/boxes/">Primitive: Boxes</a></li>
      <li><a href="primitives/cylinders/">Primitive: Cylinders</a></li>
      <li><a href="primitives/defaults/">Primitive: Defaults</a></li>
      <li><a href="primitives/images/">Primitive: Images</a></li>
      <li><a href="primitives/models/">Primitive: Models <em>(glTF, OBJ, COLLADA)</em></a></li>
      <li><a href="primitives/planes/">Primitive: Planes</a></li>
      <li><a href="primitives/ring/">Primitive: Ring</a></li>
      <li><a href="primitives/torus/">Primitive: Torus</a></li>
      <li><a href="test/raycaster/">Raycaster</a></li>
      <li><a href="test/raycaster/simple.html">Raycaster (Simple)</a></li>
      <li><a href="test/shaders/">Shaders</a></li>
      <li><a href="test/shadows/">Shadows</a></li>
      <li><a href="test/text/">Text</a></li>
      <li><a href="test/text/anchors.html">Text Anchors</a></li>
      <li><a href="test/text/msdf.html">Text Fonts <em>(MSDF vs. SDF)</em></a></li>
      <li><a href="test/text/scenarios.html">Text Scenarios</a></li>
      <li><a href="test/text/sizes.html">Text Sizes</a></li>
      <li><a href="test/towers/">Towers</a></li>
      <li><a href="test/video/">Video</a></li>
      <li><a href="test/videosphere/">Video 360&deg;</a></li>
      <li><a href="test/visibility/">Visibility</a></li>
    </ul>

    <h2>Performance</h2>

    <ul class="links">
      <li><a href="performance/animation/">Animation</a></li>
      <li><a href="performance/cubes/">Cubes</a></li>
      <li><a href="performance/entity-count/">Entity Count</a></li>
      <li><a href="performance/in-vr/">In VR</a></li>
    </ul>
  </body>
</html>