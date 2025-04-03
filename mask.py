import matplotlib.pyplot as plt
import rasterio
from rasterio.features import rasterize
import numpy as np

class Mask():

    def __init__(self, gdf, width=1024, height=1024):
        self.gdf = gdf
        self.width = width
        self.height = height
        self.mask = self._gen_mask(gdf, self.width, self.height)

    @staticmethod
    def _gen_mask(gdf, width, height):
        bounds = gdf.total_bounds

        transform = rasterio.transform.from_bounds(*bounds, width, height)
        mask = rasterize(
            [(geom, 1) for geom in gdf.geometry],
            out_shape=(height, width),
            transform=transform,
            fill=0,
            dtype=np.uint8
        )
        
        return mask
    
    def visualize(self):
        fig, ax = plt.subplots(figsize=(10, 10))

        plt.imshow(self.mask, cmap='gray', alpha=0.5)

        self.gdf.boundary.plot(ax=ax, edgecolor='red', linewidth=1)

        plt.title("Geospatial Mask")
        plt.axis('off')
        plt.show()

    def save(self, output_path):
        """Optional: Save the raster mask as a GeoTIFF file."""
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=self.mask.shape[0],
            width=self.mask.shape[1],
            count=1,
            dtype=np.uint8,
            crs=self.gdf.crs,
            transform=self.transform
        ) as dst:
            dst.write(self.mask, 1)