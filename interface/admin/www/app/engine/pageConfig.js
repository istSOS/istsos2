Ext.ns("istsos","istsos.engine");

/*
    istFunction: {
        onLoad: "operationPost",
        onSubmit: "operationPost"
    },
    istOperation: {
        restUrl: wa.url + "/istsos/services",
        onLoadMethod: "GET",
        onSubmitMethod: "PUT"
    }
*/

istsos.EMPTY = "EMPTY";
istsos.SUBMIT = "SUBMIT";

// execute a next page operation without executing any other service operation
istsos.WIZARD_JUST_NEXT = "WIZARD_JUST_NEXT";
istsos.WIZARD = "WIZARD";
istsos.WIZARD_NEXT_FINISH = "WIZARD_NEXT_FINISH";
istsos.WIZARD_FINISH = "WIZARD_FINISH";

istsos.engine.serviceConfig = {
    "Service Settings": {
        "Database": {
            istTitle: "Database",
            icon: 'database.svg',
            istBody: ["istsos.view.database"],
            istOperation: wa.url + "/istsos/services/@/configsections/connection",
            istFooter: istsos.SUBMIT
        },
        "Service provider": {
            istTitle: "Service provider",
            icon: 'provider.svg',
            istBody: ["istsos.view.provider"],
            istOperation: wa.url + "/istsos/services/@/configsections/provider",
            istFooter: istsos.SUBMIT
        },
        "Service identification": {
            istTitle: "Service identification",
            icon: 'contacts.svg',
            istBody: ["istsos.view.identification"],
            istOperation: wa.url + "/istsos/services/@/configsections/identification",
            istFooter: istsos.SUBMIT
        },
        "Coordinates system": {
            istTitle: "Coordinates",
            icon: 'coordinate.svg',
            istBody: ["istsos.view.geo"],
            istOperation: wa.url + "/istsos/services/@/configsections/geo",
            istFooter: istsos.SUBMIT
        },/*
        "MQTT Publisher": {
            istTitle: "MQTT Publisher",
            icon: 'mqtt.svg',
            istBody: ["istsos.view.mqtt"],
            istOperation: wa.url + "/istsos/services/@/configsections/mqtt",
            istFooter: istsos.SUBMIT
        },*/
        "GetObservation Configuration": {
            istTitle: "GetObservation Configuration",
            icon: 'getobs.svg',
            istBody: ["istsos.view.getobservation"],
            istFunction: {
                onLoad: "executeGet",
                onSubmit: "executePost"
            },
            //istOperation: wa.url + "/istsos/services/@/configsections/getobservation",
            istFooter: istsos.SUBMIT
        },
        "Proxy Configuration": {
            istTitle: "Proxy Configuration",
            icon: 'proxy.svg',
            istBody: ["istsos.view.serviceurl"],
            istOperation: wa.url + "/istsos/services/@/configsections/serviceurl",
            istFooter: istsos.SUBMIT
        }
    },
    "Wizards": {
        "Offerings": {
            istTitle: "Offerings editor",
            icon: 'offerings.svg',
            istBody: ["istsos.view.offeringsEditor"],
            istFunction: {
                onLoad: "operationLoad"
            },
            istFooter: istsos.EMPTY
        },
        "Procedures": {
            istTitle: "Procedures",
            icon: 'system-run.svg',
            istDescription: "Click on procedure name to edit",
            istBody: ["istsos.view.proceduresList"],
            istFunction: {
                onLoad: "operationLoad"
            },
            istFooter: istsos.EMPTY
        },
        "Virtual Procedures": {
            istTitle: "Virtual Procedures",
            icon: 'virtual.svg',
            istBody: ["istsos.view.VirtualProcedureEditor"],
            wapage: 'MainCenter',
            istFooter: istsos.EMPTY
        },
        "New procedure": {
            istTitle: "New procedure",
            icon: 'new_service.svg',
            istBody: ["istsos.view.procedure"],
            istFunction: {
                onSubmit: "executePost"
            },
            istFooter: istsos.SUBMIT
        },
        "Observed properties": {
            istTitle: "Observed properties",
            icon: 'observedProperties.svg',
            istBody: ["istsos.view.obsPropEditor"],
            istFunction: {
                onLoad: "operationLoad"
            },
            istFooter: istsos.EMPTY
        },
        "Units of measures": {
            istTitle: "Units of measures",
            icon: 'unit.svg',
            istBody: ["istsos.view.uomsEditor"],
            istFunction: {
                onLoad: "operationLoad"
            },
            istFooter: istsos.EMPTY
        },
        "Data quality": {
            istTitle: "Data quality",
            icon: 'quality_index.svg',
            istBody: ["istsos.view.qualityindexEditor"],
            istFunction: {
                onLoad: "operationLoad"
            },
            istFooter: istsos.EMPTY
        }
    }
};

istsos.engine.defaultConfig = {
    "Server": {
        "About istSOS": {
            istTitle: "About istSOS",
            icon: 'about_grey.svg',
            istBody: ["istsos.view.about"],
            istFunction: {
                onLoad: "operationLoad"
            },
            istOperation: wa.url + "/istsos/operations/about",
            istFooter: istsos.EMPTY
        },
        "Status": {
            istTitle: "Server Status",
            istDefault: "defaultPage",
            icon: 'status_1.svg',
            istDescription: "Summary of istSOS instances and run-time status",
            istBody: ["istsos.view.status"],
            istFunction: {
                onLoad: "operationLoad"
            },
            istFooter: istsos.EMPTY
        }
    },
    "Default Settings": {
        "Database": {
            istTitle: "Database",
            icon: 'database.svg',
            istBody: ["istsos.view.database"],
            istOperation: wa.url + "/istsos/services/default/configsections/connection",
            istFooter: istsos.SUBMIT
        },
        "Service provider": {
            istTitle: "Service provider",
            icon: 'provider.svg',
            istBody: ["istsos.view.provider"],
            istOperation: wa.url + "/istsos/services/default/configsections/provider",
            istFooter: istsos.SUBMIT
        },
        "Service identification": {
            istTitle: "Service identification",
            icon: 'contacts.svg',
            istBody: ["istsos.view.identification"],
            istOperation: wa.url + "/istsos/services/default/configsections/identification",
            istFooter: istsos.SUBMIT
        },
        "Coordinates system": {
            istTitle: "Contacts",
            icon: 'coordinate.svg',
            istBody: ["istsos.view.geo"],
            istOperation: wa.url + "/istsos/services/default/configsections/geo",
            istFooter: istsos.SUBMIT
        },/*
        "MQTT Publisher": {
            istTitle: "MQTT Publisher",
            icon: 'mqtt.svg',
            istBody: ["istsos.view.mqtt"],
            istOperation: wa.url + "/istsos/services/default/configsections/mqtt",
            istFooter: istsos.SUBMIT
        },*/
        "GetObservation Configuration": {
            istTitle: "GetObservation Configuration",
            icon: 'getobs.svg',
            istBody: ["istsos.view.getobservation"],
            istOperation: wa.url + "/istsos/services/default/configsections/getobservation",
            istFooter: istsos.SUBMIT
        },
        "Proxy Configuration": {
            istTitle: "Proxy Configuration",
            icon: 'proxy.svg',
            istBody: ["istsos.view.serviceurl"],
            istOperation: wa.url + "/istsos/services/default/configsections/serviceurl",
            istFooter: istsos.SUBMIT
        }
    },
    "Wizards": {
        "New service": {
            istTitle: "New service",
            icon: 'new_service.svg',
            wizardName: "newservice",
            wapage: 'WizardPage',
            istFooter: istsos.EMPTY
        },
        "Delete service": {
            istTitle: "Delete service",
            icon: 'delete2.svg',
            istBody: ["istsos.view.serviceEditor"],
            istFunction: {
                onLoad: "operationLoad"
            },
            istFooter: istsos.EMPTY
        }
    }
};

istsos.engine.observationConfig = {
    "Services": {
        "Data Editor": {
            istTitle: "Data Editor",
            icon: 'editor.svg',
            istBody: ["istsos.view.Editor1"],
            wapage: 'MainCenter',
            istFooter: istsos.EMPTY
        },
        "Data Viewer": {
            istTitle: "Data Viewer",
            icon: 'editor.svg',
            istBody: ["istsos.view.ViewerPanel"],
            wapage: 'MainCenter',
            istFooter: istsos.EMPTY
        }
    }
}

istsos.engine.pageWizard = {
    /*"initialization": {
        "Welcome": {
            istTitle: "Welcome",
            istDescription: "Hi,<br>istSOS manager needs some configuration before running correctly",
            istBody: "Please follow the setup instruction to start using the formidable istSOS manager!!.",
            istFooter: istsos.WIZARD_JUST_NEXT
        },
        "defaultDatabase": {
            istTitle: "Default database connection",
            istDescription: "Fill the parameter required to connect to your database:<br><br>" +
            "If the database name does not exist this procedure will create a " +
            "new one and then it will be used to store istSOS data and " +
            "configuration for each service instance.",
            istBody: ["istsos.view.database"],
            istOperation: {
                restUrl: wa.url + "/istsos/services/@/configsections/connection",
                onSubmitMethod: "PUT"
            },
            istFooter: istsos.WIZARD_NEXT_FINISH
        },
        "defaultProvider": {
            istTitle: "Default Service Provider",
            istDescription: "Please fill the following parameters.",
            istBody: ["istsos.view.provider"],
            istOperation: {
                restUrl: wa.url + "/istsos/services/default/configsections/provider",
                onSubmitMethod: "PUT"
            },
            istFooter: istsos.WIZARD
        },
        "defaultIdentification": {
            istTitle: "Default Service Identification",
            istDescription: "Please fill the following parameters:<br><ul>" +
            "<li>istSOS library path: this is the folder where...</li>"+
            "</ul>",
            istBody: ["istsos.view.identification"],
            istOperation: {
                restUrl: wa.url + "/istsos/services/default/configsections/identification",
                onSubmitMethod: "PUT"
            },
            istFooter: istsos.WIZARD
        },
        "defaultCoordinates": {
            istTitle: "Default Coordinates system",
            istDescription: "Please fill the following parameters:<br><ul>" +
            "<li>istSOS library path: this is the folder where...</li>"+
            "</ul>",
            istBody: ["istsos.view.geo"],
            istOperation: {
                restUrl: wa.url + "/istsos/services/default/configsections/geo",
                onSubmitMethod: "PUT"
            },
            istFooter: istsos.WIZARD
        },
        "defaultGetobservation": {
            istTitle: "Default GetObservation Configuration",
            istDescription: "Please fill the following parameters:<br><ul>" +
            "<li>istSOS library path: this is the folder where...</li>"+
            "</ul>",
            istBody: ["istsos.view.getobservation"],
            istOperation: {
                restUrl: wa.url + "/istsos/services/default/configsections/getobservation",
                onSubmitMethod: "PUT"
            },
            istFooter: istsos.WIZARD
        },
        "newServiceWizard": {
            istTitle: "Initialize a new service",
            istDescription: "This proceduce will guide you in each step needed to configure a new Sensor Observation Service.",
            istBody: "Please follow the setup instruction to start using it.",
            istFooter: istsos.WIZARD_JUST_NEXT
        },
        "newServiceName": {
            istTitle: "Initialize a new service",
            istDescription: "This proceduce will guide you in each step needed to configure a new Sensor Observation Service.",
            istBody: ["istsos.view.newservice"],
            istFunction: {
                onLoad: "operationLoad",
                onSubmit: "operationPost"
            },
            istBodyOnSubmit: "test",
            istFooter: istsos.WIZARD
        },
        "newServicePersonalization": {
            istTitle: "Service personalization",
            istDescription: "Now you can personalize this istSOS instance otherwise the default server setting will be used.",
            istBody: ["istsos.view.serviceconfig"],
            istFunction: {
                onLoad: "operationLoad",
                onSubmit: "operationPost"
            },
            istFooter: istsos.WIZARD
        },
        "newServiceComplete": {
            istTitle: "Configuration complete",
            istDescription: "Now you are able to use your istSOS.",
            istFooter: istsos.WIZARD_FINISH
        }
    },*/
    "newservice": {
        "newServiceWizard": {
            istTitle: "Initialize a new service",
            istDescription: "This proceduce will guide you in each step needed to configure a new Sensor Observation Service.",
            istBody: "Please follow the setup instruction to start using it.",
            istFooter: istsos.WIZARD_JUST_NEXT
        },
        "newServiceName": {
            istTitle: "Initialize a new service",
            istDescription: "This proceduce will guide you in each step needed to configure a new Sensor Observation Service.",
            istBody: ["istsos.view.newservice"],
            istFunction: {
                onLoad: "operationLoad",
                onSubmit: "operationPost"
            },
            istBodyOnSubmit: "test",
            istFooter: istsos.WIZARD
        },
        "newServicePersonalization": {
            istTitle: "Service personalization",
            istDescription: "Now you can personalize this istSOS instance otherwise the default server setting will be used.",
            istBody: ["istsos.view.serviceconfig"],
            istFunction: {
                onLoad: "operationLoad",
                onSubmit: "operationPost"
            },
            istFooter: istsos.WIZARD
        },
        "newServiceComplete": {
            istTitle: "Configuration complete",
            istDescription: "Now you are able to use your istSOS.",
            istFooter: istsos.WIZARD_FINISH
        }
    }
};
