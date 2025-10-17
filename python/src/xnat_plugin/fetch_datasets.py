from typing import Optional
import pooch
from pathlib import Path


def _set_up_zenodo_doi(base_url: str):
    ZENODO = pooch.create(
        path=Path(__file__).parents[3] / "test-data",
        base_url=base_url,
        registry=None,
        retry_if_failed=5,
    )
    ZENODO.load_registry_from_doi()
    return ZENODO


def _fetch_from_zenodo(
    base_url: str,
    image_name: str,
    zip_file: Optional[str] = None,
    download_all: Optional[bool] = None,
) -> Path:
    """Fetch mrd file from zenodo (if not already cached), and return the file path where
    data is downloaded"""

    ZENODO = _set_up_zenodo_doi(base_url)

    if zip_file:
        if download_all:
            unpack = pooch.Unzip(members=[zip_file])
            ZENODO.fetch(f"{zip_file}.zip", processor=unpack)
            image_path = ZENODO.path / f"{zip_file}.zip.unzip" / zip_file / image_name
        else:
            unpack = pooch.Unzip(members=[image_name])
            image_path = Path(ZENODO.fetch(f"{zip_file}.zip", processor=unpack)[0])

    else:
        image_path = Path(ZENODO.fetch(image_name))

    return image_path


def get_single_file() -> Path:
    """Fetch mrd file with multiple datasets, or return cached path if already present."""
    test_data_dir = Path(__file__).parents[3] / "test-data"
    image_path = test_data_dir / "cart_t1_msense_integrated.mrd"
    if image_path.exists():
        return image_path
    return _fetch_from_zenodo(
        "doi:10.5281/zenodo.15223816",
        "cart_t1_msense_integrated.mrd",
    )


def get_single_file_from_zip() -> Path:
    """Fetch mrd file with a single dataset, or return cached path if already present."""

    test_data_dir = (
        Path(__file__).parents[3]
        / "test-data"
        / "PTB_ACRPhantom_GRAPPA.zip.unzip"
        / "PTB_ACRPhantom_GRAPPA"
    )
    image_path = test_data_dir / "ptb_resolutionphantom_fully_ismrmrd.h5"
    if image_path.exists():
        return image_path
    return _fetch_from_zenodo(
        "doi:10.5281/zenodo.2633785",
        "PTB_ACRPhantom_GRAPPA/ptb_resolutionphantom_fully_ismrmrd.h5",
        zip_file="PTB_ACRPhantom_GRAPPA",
        download_all=False,
    )


def get_all_files_from_zip() -> Path:
    """Fetch interfile file with a single dataset, or return cached path if already present."""

    test_data_dir = Path(__file__).parents[3] / "test-data"
    image_path = test_data_dir / "NEMA_IQ" / "20170809_NEMA_60min_UCL.l.hdr"

    if image_path.exists():
        return image_path
    return _fetch_from_zenodo(
        "doi:10.5281/zenodo.1304454",
        "20170809_NEMA_60min_UCL.l.hdr",
        zip_file="NEMA_IQ",
        download_all=True,
    )
