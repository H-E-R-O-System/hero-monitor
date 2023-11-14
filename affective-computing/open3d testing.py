import open3d as o3d

# sample_ply_data = o3d.data.PLYPointCloud()
pcd = o3d.io.read_point_cloud("sync.ply")
pcd.paint_uniform_color([1, 0.706, 0])
o3d.visualization.draw_geometries([pcd])