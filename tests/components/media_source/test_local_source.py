"""Test Local Media Source."""
import pytest

from homeassistant.components import media_source
from homeassistant.components.media_source import const
from homeassistant.config import async_process_ha_core_config
from homeassistant.setup import async_setup_component


async def test_async_browse_media(hass):
    """Test browse media."""
    await async_process_ha_core_config(hass, {})
    await hass.async_block_till_done()

    assert await async_setup_component(hass, const.DOMAIN, {})
    await hass.async_block_till_done()

    # Test path not exists
    with pytest.raises(media_source.BrowseError) as excinfo:
        await media_source.async_browse_media(
            hass, f"{const.URI_SCHEME}{const.DOMAIN}/media/test/not/exist"
        )
    assert str(excinfo.value) == "Path does not exist."

    # Test browse file
    with pytest.raises(media_source.BrowseError) as excinfo:
        await media_source.async_browse_media(
            hass, f"{const.URI_SCHEME}{const.DOMAIN}/media/test.mp3"
        )
    assert str(excinfo.value) == "Path is not a directory."

    # Test invalid base
    with pytest.raises(media_source.BrowseError) as excinfo:
        await media_source.async_browse_media(
            hass, f"{const.URI_SCHEME}{const.DOMAIN}/invalid/base"
        )
    assert str(excinfo.value) == "Unknown source directory."

    # Test directory traversal
    with pytest.raises(media_source.BrowseError) as excinfo:
        await media_source.async_browse_media(
            hass, f"{const.URI_SCHEME}{const.DOMAIN}/media/../configuration.yaml"
        )
    assert str(excinfo.value) == "Invalid path."

    # Test successful listing
    media = await media_source.async_browse_media(
        hass, f"{const.URI_SCHEME}{const.DOMAIN}/media/."
    )
    assert media


async def test_media_view(hass, hass_client):
    """Test media view."""
    await async_process_ha_core_config(hass, {})
    await hass.async_block_till_done()

    assert await async_setup_component(hass, const.DOMAIN, {})
    await hass.async_block_till_done()

    client = await hass_client()

    # Protects against non-existent files
    resp = await client.get("/local_source/media/invalid.txt")
    assert resp.status == 404

    # Protects against non-media files
    resp = await client.get("/local_source/media/not_media.txt")
    assert resp.status == 404

    # Fetch available media
    resp = await client.get("/local_source/media/test.mp3")
    assert resp.status == 200
