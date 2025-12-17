# Object Detection Flask

run `.\run_services.ps1` to run all servers  
access ui on `localhost:5000`

## Services:
### Frontend
1. UI interface for the user
2. User can upload image, view, process and save results.


## Files
| S.No | File | Description |
| - | - | - |
| 1 | `uuid.ext` | The original file as uploaded by user|
| 2 | `mapping.pkl` |Store mapping between uuid and original file name. Frontend writes this file while uploading.|
| 3 | `uuid.npy` | Image stored as an `np.ndarray` for faster fetch and processing. All images will be saved as this and processing will be done on this. Extending support for more extensions is trivial |
| 4 | `uuid.pkl` | File details written storing info about what processing has been done so can be used as cache. Also stores raster details like profile, crs, etc. in case of .tif. |
| 5 | `uuid.process.npy` | Processed File | 


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

### Image Rendering
> Renders image on the central screen
1. Selecting an image from the `image-list` panel renders the image in full resolution to the center section.
2. The image viewer allows for infinite zoom and pan.
3. Image is rendered raw PNG without any pixel interpolation.
4. Any transformation / edit to the image locks the image and restricts selection of other images from the `image-list` panel.
5. At any given time, the system only maintains a single central image stack per session.
6. User can perform any update on the image incrementally and the latest version is rendered on screen.
7. User can save the latest image as png, jpeg or tiff. Defaults to the original image type but can be changed as per the user.

### Image Editing / Transformation
> Flow for transformation of selected image.
1. Backend keeps track of the follwing details 

| Variable | Description |
| - | - |
| Stack | Keeps track of npy file ids as intermediate process output |
| Transforms | Keeps track of transformation objects that provides details on which transformation and parameters. Length of this is always 1 less than stack
| Image Pointer | The index of the current rendered image on the UI. Useful for undo and redo. Doing a transformation on an image not at the end would clear the stack after the current pos. |

2. The frontend and backend are strongly coupled so there's only one session per backend service. This means, opening multiple tabs of the frontend renders the same way and affects all screens.
3. The frontend explicitly controls when the central image can be changed and when the stack should be cleared.