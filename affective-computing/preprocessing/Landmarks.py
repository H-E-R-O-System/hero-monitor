import open3d as o3d

class Landmarks:
    def __init__(self, ptCouldIn):
        leftEyeIDs = [134, 174, 158, 159, 160, 161, 162, 247, 34, 8, 164,
                      145, 146, 154, 155, 156]

        rightEyeIDs = [363, 399, 385, 386, 387, 388, 389, 467, 264,
                       250, 391, 374, 375, 381, 382, 383]

        eyeIDs = leftEyeIDs + rightEyeIDs

        mouthIDs = [292, 410, 271, 270, 268, 1, 38, 40, 41, 186, 62, 147,
                    92, 182, 85, 18, 315, 406, 322, 376, 309, 416, 311, 312,
                    313, 14, 83, 82, 81, 192, 79, 96, 89, 179, 88,
                    15, 318, 403, 319, 325]

        rightEyebrowIDs = [337, 296, 297, 283, 335, 284, 294, 277, 301]

        leftEyebrowIDs = [108, 66, 67, 106, 53, 54, 64, 47, 71]

        eyebrowIDs = leftEyebrowIDs + rightEyebrowIDs
        leftCheekIDs = [51, 119]
        rightCheekIDs = [281, 348]
        cheekIDs = leftCheekIDs + rightCheekIDs

        keypoints = mouthIDs + eyeIDs + eyebrowIDs + cheekIDs

        self.all = o3d.geometry.PointCloud()
        self.all.points = o3d.utility.Vector3dVector(ptCouldIn[keypoints, :])

        self.mouth = o3d.geometry.PointCloud()
        self.mouth.points = o3d.utility.Vector3dVector(ptCouldIn[mouthIDs, :])
        self.eyes = o3d.geometry.PointCloud()
        self.eyes.points = o3d.utility.Vector3dVector(ptCouldIn[eyeIDs, :])
        self.eyebrows = o3d.geometry.PointCloud()
        self.eyebrows.points = o3d.utility.Vector3dVector(ptCouldIn[eyebrowIDs, :])
        self.cheeks = o3d.geometry.PointCloud()
        self.cheeks.points = o3d.utility.Vector3dVector(ptCouldIn[cheekIDs, :])

        self.left_eye = o3d.geometry.PointCloud()
        self.left_eye.points = o3d.utility.Vector3dVector(ptCouldIn[leftEyeIDs, :])
        self.right_eye = o3d.geometry.PointCloud()
        self.right_eye.points = o3d.utility.Vector3dVector(ptCouldIn[rightEyeIDs, :])
        self.left_eyebrow = o3d.geometry.PointCloud()
        self.left_eyebrow.points = o3d.utility.Vector3dVector(ptCouldIn[leftEyebrowIDs, :])
        self.right_eyebrow = o3d.geometry.PointCloud()
        self.right_eyebrow.points = o3d.utility.Vector3dVector(ptCouldIn[rightEyebrowIDs, :])

