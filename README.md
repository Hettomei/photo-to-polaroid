Convert picture into polaroid

# Install

requires python >= 3.9

```
pip install -r requirement.

python polaroid.py --help
```


# Demo

```
python polaroid.py --from examples --to examples-after --final-width 400
```

![demo1-pola](examples-after/pexels-alexis-ricardo-alaurin-10103566-portrait.jpg)
![demo2-pola](examples-after/pexels-olia-danilevich-6149104-landscape.jpg)
![demo3-pola](examples-after/too_little.jpg)


```
python polaroid.py --from examples --to examples-after-no-crop --final-width 400 --no-crop
```

![demo1-pola-no-crop](examples-after-no-crop/pexels-alexis-ricardo-alaurin-10103566-portrait.jpg)
![demo2-pola-no-crop](examples-after-no-crop/pexels-olia-danilevich-6149104-landscape.jpg)
![demo3-pola-no-crop](examples-after-no-crop/too_little.jpg)
