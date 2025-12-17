# Image Processing Flask App

> A simple app to run any transformation on a single image. The supported transformations and image types can be extended trivially.

run `.\run_services.ps1` to run all servers  
access ui on `localhost:5000`

## High Level Flow
1. The intention is to build an interface where any image can be transformed via a function.
2. As images can be of multiple formats, the app converts any supported image into a standard `.npy` file (`np.ndarray`) for future processing.
3. All functions and tranformations are defined to work with an `np.ndarray` object and its parameters.
4. The output of each transformation is also a `np.ndarray`.
5. Support for new file types can be extended easily by adding a parser to convert the file to `np.ndarray`.
6. Support for new transformation can be extended by adding a new transformation function and updating config file in `Frontend/static`
7. The application allows to infinitely linear stack transformation on an image  
```- --> Image -> Transform -> Image - -->```
8. The images are rendered in `uint8` for the first 3 bands. Image rendering is independent and does not affect the actual file. For example, an a `16bit` image with 4 bands will be rendered as an `8 bit` image using its first 3 bands only. This render image is derived from the main image and does not affect the original.

## File and Directory Description

| Directory | Description |
| - | - |
| /Services | Contains individual services and their associated codes |
| /Services/\<Service> | The individual service housing the `app.py` which starts the individual service
| /Helpers | Contains global classes and helper functions applicable to all services |
| /Data/Uploads | All files uploaded from the UI are copied here by default. Location can be changed in `.env`.
| /Data/Session/Stack | Contains details of the current stack such as transformation history and intermediate canonical npy files. Read more in `transformation flow`

| File | Description |
| - | - |
| `run_services.ps1` | Simple powershell script to launch all services at once. Run this to start all services easily. ll|
| `main.py` | Can be **ignored**, not used during app building or usage. Used as test script. |
| `.env` | Environment variables used globally by all services |
| `/Services/Service/app.py` | The entry point for the service app. Has the routes for each service api |
| `/Services/Service/helpers.py` | Has functions to handle functionality for each api |
| `/Helpers/common-helpers.py` | Contains generic function used across services |


| Class | Description |
| - | - |
| File | Parent Class to manage files. In `Helpers.FileClass.file.File` |
| ImageFile | Imports File Class. Converts images to standard `.npy` and generates `.pkl` for them. In `Helpers.FileClass.file.ImageFile` |
| StackManager | Object manages the stack that tracks current view image, undo, redo, functionality, image stack etc. In `Helpers.StackManager.stackManager.StackManager` |
| Transformation (__WIP__) | Simple object notation to store info about a single transformation. In `Helpers.TransformationClass.transformation.Transformation`.  |



## Flow
### File upload
> Allows user to upload a single file and then do further work on the same.

1. User clicks on `Upload Image` on UI.
2. Frontend generates a `uuid` of the image
3. Frontend stores a copy of the file as `uuid.ext` to `Data/Uploads`
4. Frontend updates `mapping.pkl` to include the image map from uuid -> file_name
5. Frontend calls Backend with the uuid for parsing
6. Backend opens the file and parses it based on the file extension.
7. After successful parsing a new file `uuid.npy` and `uuid.pkl` are generated.
8. `uuid.npy` contains the image as an `np.ndarray` which should be considered standard processing input for any transformation, inference or edits
9. `uuid.pkl` contains class and meta information which can be extended per requirement. Ideally it would contain info about file extension, geo info if any, dtypes, etc.

| File | Description |
| - | - |
| `/Data/Uploads/uuid.ext` | The original file as uploaded by user|
| `/Data/Uploads/mapping.pkl` |Store mapping between uuid and original file name. Frontend writes this file while uploading.|
| `/Data/Uploads/uuid.npy` | Image stored as an `np.ndarray` for faster fetch and processing. All images will be saved as this and processing will be done on this. Extending support for more extensions is trivial |
| `/Data/Uploads/uuid.pkl` | File details written storing info about what processing has been done so can be used as cache. Also stores raster details like profile, crs, etc. in case of .tif. |

### Image Rendering
> Renders image on the central screen
1. Selecting an image from the `image-list` panel renders the image in full resolution to the center section.
2. The image viewer allows for infinite zoom and pan.
3. Image is rendered raw PNG without any pixel interpolation.
4. Any transformation / edit to the image locks the image and restricts selection of other images from the `image-list` panel.
5. At any given time, the system only maintains a single central image stack per session.
6. User can perform any update on the image incrementally and the latest version is rendered on screen.
7. __TODO:__ User can save the latest image as png, jpeg or tiff. Defaults to the original image type but can be changed as per the user.
8. The images are rendered in `uint8` for the first 3 bands. Image rendering is independent and does not affect the actual file. For example, an a `16bit` image with 4 bands will be rendered as an `8 bit` image using its first 3 bands only. This render image is derived from the main image and does not affect the original.

### Image Editing / Transformation
> Flow for transformation of selected image.
1. The application allows to infinitely linear stack transformation on an image  
```
~ - --> Image -> Transform -> Image ~ - -->
          |                     |
          v                     v
        Render                Render
```
2. Backend initialises a `StackManager` that retrieves previous session if relevant.

> All file here are in the Director: `/Data/Session/Stack`

| File | Description |
| - | - |
| `stack.pkl` | The pickled `StackManager` object. If this exists, the stack manager is initialised based on this. |
| `uuid.npy` | `.npy` file generated for each image in the stack. |

> Variables stored in the `StackManager` object

| Stack Manager Variables | Type | Description |
| - | - | - | 
| `npy_stack` | `list[str]` | Keeps track of npy file ids within the stack. These are outputs after individual transformations. Used during `undo` and `redo` |
| `parent_uuid` | `str` | The `uuid` of the parent file. This is used to fetch meta info such as original file types, raster details, etc. This `uuid` maps to the Uploads dir and not the Stack dir |
| `current_pointer` | `int` | Stores the index of the current rendered image within the stack |
| `__png_cache` | `dict[int, bytes]` | Stores the indermediate npy files as 8bit 3 band bytes for faster rendering. This is required as render conversion for large images in different dtypes take significant cpu time | 

2. The frontend and backend are strongly coupled so there's only one session per backend service. This means, opening multiple tabs of the frontend renders the same way and affects all screens.
3. The frontend explicitly controls when the central image can be changed and when the stack should be cleared.

### Extending transformations
1. Backend takes tranformation requests on `PUT /transform` as a single generic json and forwards to ImageOperation.
2. ImageOperation receives the request and validates the request.
3. `ImagerOperation.helpers.transform` is a `dict` that maps operation string to its associated function. Extend support for new transformations by inserting a new pair to this dict.
4. `Services/Frontend/static/ops_config.jsonc` contains the config file that renders transformation menus and forms on the UI. Ensure that the parameter and operation names strictly match the imlementation in `ImageOperations`

## Services:
### Frontend
1. UI interface for the user
2. User can upload image, view, process and save results.

### 