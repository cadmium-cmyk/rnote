# Rnote File Format Specification

The `.rnote` file format is a gzipped JSON file. At the root, it contains a wrapper with a version and the data.

## Root Structure

```json
{
  "version": "0.15.0",
  "data": { ... }
}
```

The `data` field contains the serialized `RnoteFileMaj0Min15` object, which encapsulates the `engine_snapshot`.

## `RnoteFileMaj0Min15` (struct)

| Field | Type | Description |
|---|---|---|
| `engine_snapshot` | `ijson::IValue` | A snapshot of the engine. |

## `Document` (struct)

| Field | Type | Description |
|---|---|---|
| `config` | `DocumentConfig` |  |
| `x` | `f64` |  |
| `y` | `f64` |  |
| `width` | `f64` |  |
| `height` | `f64` |  |

## `DocumentConfig` (struct)

| Field | Type | Description |
|---|---|---|
| `format` | `Format` |  |
| `background` | `Background` |  |
| `layout` | `Layout` |  |

## `Format` (struct)

| Field | Type | Description |
|---|---|---|
| `width` | `f64` |  |
| `height` | `f64` |  |
| `dpi` | `f64` |  |
| `orientation` | `Orientation` |  |
| `border_color` | `Color` |  |
| `show_borders` | `bool` |  |
| `show_origin_indicator` | `bool` |  |

## `Orientation` (enum)

| Variant | Type | Description |
|---|---|---|
| `portrait` | `` |  |
| `landscape` | `` |  |

## `Background` (struct)

| Field | Type | Description |
|---|---|---|
| `color` | `Color` |  |
| `pattern` | `PatternStyle` |  |
| `pattern_size` | `Vector2` |  |
| `pattern_color` | `Color` |  |

## `EngineSnapshot` (struct)

| Field | Type | Description |
|---|---|---|
| `document` | `Document` |  |
| `camera` | `Camera` |  |
| `stroke_components` | `Arc<SlotMap<StrokeKey, Arc<Stroke>>>` |  |
| `chrono_components` | `Arc<SecondaryMap<StrokeKey, Arc<ChronoComponent>>>` |  |
| `chrono_counter` | `u32` |  |

## `Camera` (struct)

| Field | Type | Description |
|---|---|---|
| `offset` | `Vector2` | The offset in surface coordinates. |
| `size` | `Vector2` | The dimensions in surface coordinates. |
| `zoom` | `f64` | The camera zoom, origin at (0.0, 0.0). |
| `temporary_zoom` | `f64` | The temporary zoom. Is used to overlay the "permanent" zoom. |
| `scale_factor` | `f64` | The scale factor of the surface, usually 1.0 or 2.0 for high-dpi screens.  This value could become a non-integer value in the future, so it is stored as float. |
| `zoom_task_handle` | `Option<crate::tasks::OneOffTaskHandle>` |  |

## `Stroke` (enum)

| Variant | Type | Description |
|---|---|---|
| `brushstroke` | `(BrushStroke)` |  |
| `shapestroke` | `(ShapeStroke)` |  |
| `textstroke` | `(TextStroke)` |  |
| `vectorimage` | `(VectorImage)` |  |
| `bitmapimage` | `(BitmapImage)` |  |

## `BrushStroke` (struct)

| Field | Type | Description |
|---|---|---|
| `path` | `PenPath` |  |
| `style` | `Style` |  |
| `hitboxes` | `Vec<Aabb>` |  |

## `PenPath` (struct)

a pen path, consisting of segments of pen input elements

| Field | Type | Description |
|---|---|---|
| `start` | `Element` | The path start |
| `segments` | `Vec<Segment>` | The segments |

## `Element` (struct)

A pen input element.

| Field | Type | Description |
|---|---|---|
| `pos` | `Vector2` | The position of the element. |
| `pressure` | `f64` | The pen pressure. The valid range is [0.0, 1.0]. |

## `Segment` (enum)

A single segment, usually of a pen path.

| Variant | Type | Description |
|---|---|---|
| `lineto` | `` | A line-to segment. |
| `quadbezto` | `` | A quadratic-bezier-to segment. |
| `cubbezto` | `` | A cubic-bezier-to segment. |

## `Style` (enum)

A style choice holding the style options inside its variants.

| Variant | Type | Description |
|---|---|---|
| `smooth` | `(SmoothOptions)` | A smooth style |
| `rough` | `(RoughOptions)` | A rough style |
| `textured` | `(TexturedOptions)` | A textured style |

## `SmoothOptions` (struct)

Options for shapes that can be drawn in a smooth style. Ensure the precursor struct used in deserialization matches this one.

| Field | Type | Description |
|---|---|---|
| `stroke_width` | `f64` | Stroke width. |
| `stroke_color` | `Option<Color>` | Stroke color. When set to None, the stroke outline is not drawn. |
| `fill_color` | `Option<Color>` | Fill color. When set to None, the fill is not drawn. |
| `pressure_curve` | `PressureCurve` | Pressure curve. |
| `line_style` | `LineStyle` | Line style. |
| `line_cap` | `LineCap` | Line cap. |
| `piet_stroke_style` | `piet::StrokeStyle` | The inner piet::StrokeStyle, computed using the stroke_width, line_style, and line_cap. |

## `RoughOptions` (struct)

Options for shapes that can be drawn in a rough style.

| Field | Type | Description |
|---|---|---|
| `stroke_color` | `Option<Color>` | Stroke color. When set to None, the stroke outline is not drawn. |
| `stroke_width` | `f64` | Stroke width. |
| `fill_color` | `Option<Color>` | Fill color. When set to None the fill is not drawn. |
| `fill_style` | `FillStyle` | Fill style. |
| `hachure_angle` | `f64` | Hachure angle (in radians). |
| `seed` | `Option<u64>` | An optional seed to generate reproducible shapes. |

## `TexturedOptions` (struct)

Options for shapes that can be drawn in a textured style.

| Field | Type | Description |
|---|---|---|
| `seed` | `Option<u64>` | An optional seed to generate reproducible shapes. |
| `stroke_width` | `f64` | Stroke width. |
| `stroke_color` | `Option<Color>` | Stroke color. When set to None, the stroke is not drawn. |
| `density` | `f64` | Amount of dots of the texture per 10x10 area. |
| `distribution` | `TexturedDotsDistribution` | Texture dots distribution type. |
| `pressure_curve` | `PressureCurve` | Pressure curve. |

## `ShapeStroke` (struct)

| Field | Type | Description |
|---|---|---|
| `shape` | `Shape` |  |
| `style` | `Style` |  |
| `hitboxes` | `Vec<Aabb>` |  |

## `Shape` (enum)

Shape, storing shape variants.

| Variant | Type | Description |
|---|---|---|
| `line` | `(Line)` | A line shape. |
| `arrow` | `(Arrow)` | An arrow shape. |
| `rect` | `(Rectangle)` | A rectangle shape. |
| `ellipse` | `(Ellipse)` | An ellipse shape. |
| `quadbez` | `(QuadraticBezier)` | A quadratic bezier curve shape. |
| `cubbez` | `(CubicBezier)` | A cubic bezier curve shape. |
| `polyline` | `(Polyline)` | A polyline shape. |
| `polygon` | `(Polygon)` | A polygon shape. |

## `Line` (struct)

A line.

| Field | Type | Description |
|---|---|---|
| `start` | `Vector2` | Start coordinate. |
| `end` | `Vector2` | End coordinate. |

## `Arrow` (struct)

All doc-comments of this file and [ArrowBuilder][crate::builders] rely on the following
graphic:

```text
tip
/|\
/ | \
/  |  \
lline |  rline
|
|
|
start
```

Where `lline`, `tip`, `start` and `rline` represent a vector of the arrow.

| Field | Type | Description |
|---|---|---|
| `start` | `Vector2` | Start of the arrow. |
| `tip` | `Vector2` | Tip of the arow. |

## `Rectangle` (struct)

A rectangle.

| Field | Type | Description |
|---|---|---|
| `cuboid` | `Cuboid` | The cuboid, specifies the extents. |
| `affine` | `DAffine2` |  |

## `Ellipse` (struct)

An Ellipse.

| Field | Type | Description |
|---|---|---|
| `radii` | `Vector2` | The radii of the ellipse. |
| `affine` | `DAffine2` |  |

## `QuadraticBezier` (struct)

A quadratic bezier curve.

| Field | Type | Description |
|---|---|---|
| `start` | `Vector2` | Start coordinates. |
| `cp` | `Vector2` | Control point coordinates. |
| `end` | `Vector2` | End coordinates. |

## `CubicBezier` (struct)

A cubic bezier curve.

| Field | Type | Description |
|---|---|---|
| `start` | `Vector2` | Start coordinate. |
| `cp1` | `Vector2` | First control point coordinate. |
| `cp2` | `Vector2` | Second control point coordinate. |
| `end` | `Vector2` | End coordinate. |

## `Polyline` (struct)

A Polyline.

| Field | Type | Description |
|---|---|---|
| `start` | `Vector2` | The polyline start |
| `path` | `Vec<Vector2>` | The polyline path |

## `Polygon` (struct)

A Polygon.

| Field | Type | Description |
|---|---|---|
| `start` | `Vector2` | The polygon start |
| `path` | `Vec<Vector2>` | The polygon path |

## `TextStroke` (struct)

| Field | Type | Description |
|---|---|---|
| `text` | `String` |  |
| `affine` | `DAffine2` |  |
| `text_style` | `TextStyle` |  |

## `TextStyle` (struct)

| Field | Type | Description |
|---|---|---|
| `font_family` | `String` |  |
| `font_size` | `f64` |  |
| `font_weight` | `u16` |  |
| `font_style` | `FontStyle` |  |
| `color` | `Color` |  |
| `max_width` | `Option<f64>` |  |
| `alignment` | `TextAlignment` |  |
| `ranged_text_attributes` | `Vec<RangedTextAttribute>` |  |

## `FontStyle` (enum)

| Variant | Type | Description |
|---|---|---|
| `regular` | `` |  |
| `italic` | `` |  |

## `TextAlignment` (enum)

| Variant | Type | Description |
|---|---|---|
| `start` | `` |  |
| `center` | `` |  |
| `end` | `` |  |
| `fill` | `` |  |

## `RangedTextAttribute` (struct)

| Field | Type | Description |
|---|---|---|
| `range` | `Range<usize>` |  |
| `attribute` | `TextAttribute` |  |

## `TextAttribute` (enum)

| Variant | Type | Description |
|---|---|---|
| `font_family` | `(String)` | The font family. |
| `font_size` | `(f64)` | The font size, in points. |
| `font_weight` | `(u16)` | The font weight. |
| `text_color` | `(Color)` | The foreground color of the text. |
| `font_style` | `(FontStyle)` | The font style. |
| `underline` | `(bool)` | Underline. |
| `strikethrough` | `(bool)` | Strikethrough. |

## `VectorImage` (struct)

| Field | Type | Description |
|---|---|---|
| `svg_data` | `String` |  |
| `intrinsic_size` | `Vector2` |  |
| `rectangle` | `Rectangle` |  |

## `BitmapImage` (struct)

| Field | Type | Description |
|---|---|---|
| `image` | `Image` | The bitmap image.  The bounds field of the image should not be used to determine the stroke bounds. Use rectangle.bounds() instead. |
| `rectangle` | `Rectangle` |  |

## `Image` (struct)

A bitmap image.

| Field | Type | Description |
|---|---|---|
| `data` | `glib::Bytes` | The image data.  Is (de)serialized with base64 encoding. |
| `rectangle` | `Rectangle` | The target rect in the coordinate space of the document. |
| `pixel_width` | `u32` | Width of the image data. |
| `pixel_height` | `u32` | Height of the image data. |
| `memory_format` | `ImageMemoryFormat` | Memory format. |

## `ImageMemoryFormat` (enum)

| Variant | Type | Description |
|---|---|---|
| `R8g8b8a8Premultiplied` | `` |  |

## `ChronoComponent` (struct)

| Field | Type | Description |
|---|---|---|
| `t` | `u32` |  |
| `layer` | `StrokeLayer` |  |

## `StrokeLayer` (enum)

| Variant | Type | Description |
|---|---|---|
| `user_layer` | `(u32)` |  |
| `highlighter` | `` |  |
| `image` | `` |  |
| `document` | `` |  |
