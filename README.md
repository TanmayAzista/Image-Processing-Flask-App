# Object Detection Flask

run `.\run_services.ps1` to run all servers  
access ui on `localhost:5000`

## Services:
### Frontend
1. UI interface for the user
2. User can upload image, view, process and save results.


## Flow
### File upload
1. User clicks on `Upload Image` on UI.
2. Frontend generates a `uuid` of the image
3. Frontend stores a copy of the file as `uuid.ext` to `Data/Uploads`
4. Frontend updates `mapping.pkl` to include the image map from uuid -> file_name
5. Frontend calls Backend with the uuid for parsing
6. Backend opens the file and parses it based on the file extension.
7. After successful parsing a new file `uuid.npy` and `uuid.pkl` are generated.
8. `uuid.npy` contains the image as an `np.ndarray` which should be considered standard processing input for any transformation, inference or edits
9. `uuid.pkl` contains class and meta information which can be extended per requirement. Ideally it would contain info about file extension, geo info if any, dtypes, etc.

---
### Files
| S.No | File | Description |
| - | - | - |
| 1 | `uuid.ext` | The original file as uploaded by user|
| 2 | `mapping.pkl` |Store mapping between uuid and original file name. Frontend writes this file while uploading.|
| 3 | `uuid.npy` | Image stored as an `np.ndarray` for faster fetch and processing. All images will be saved as this and processing will be done on this. Extending support for more extensions is trivial |
| 4 | `uuid.pkl` | File details written storing info about what processing has been done so can be used as cache. Also stores raster details like profile, crs, etc. in case of .tif. |
| 5 | `uuid.process.npy` | Processed File | 