# prova2/app

This folder contains the javascript files for the application.

# prova2/resources

This folder contains static resources (typically an `"images"` folder as well).

# prova2/overrides

This folder contains override classes. All overrides in this folder will be 
automatically included in application builds if the target class of the override
is loaded.

# prova2/sass/etc

This folder contains misc. support code for sass builds (global functions, 
mixins, etc.)

# prova2/sass/src

This folder contains sass files defining css rules corresponding to classes
included in the application's javascript code build.  By default, files in this 
folder are mapped to the application's root namespace, 'prova2'. The
namespace to which files in this directory are matched is controlled by the
app.sass.namespace property in prova2/.sencha/app/sencha.cfg. 

# prova2/sass/var

This folder contains sass files defining sass variables corresponding to classes
included in the application's javascript code build.  By default, files in this 
folder are mapped to the application's root namespace, 'prova2'. The
namespace to which files in this directory are matched is controlled by the
app.sass.namespace property in prova2/.sencha/app/sencha.cfg. 
