# Presentation materials

This directory keeps the editable presentation and poster outputs together with
their generators. Shared branding assets live in `../assets/`.

Run the generators from the repository root:

```bash
python paper/presentation/build_presentation.py
node paper/presentation/build_poster.js
```

The Python generator uses only the standard library. The poster generator
requires the `pptxgenjs` Node.js package. Both generators resolve input and
output paths from their own locations, so they do not depend on the caller's
working directory.
