const API = "http://127.0.0.1:8000";

/* -----------------------------
Navigation
------------------------------*/

function showPage(pageId){


document.querySelectorAll(".page")
    .forEach(page => page.classList.remove("active"));

document.getElementById(pageId)
    .classList.add("active");


}

/* -----------------------------
Dashboard
------------------------------*/

async function loadDashboard(){


const cases = await fetch(`${API}/cases`)
    .then(res => res.json());

const templates = await fetch(`${API}/templates`)
    .then(res => res.json());

const drafts = await fetch(`${API}/drafts`)
    .then(res => res.json());

document.getElementById("caseCount").innerText =
    cases.length;

document.getElementById("templateCount").innerText =
    templates.length;

document.getElementById("draftCount").innerText =
    drafts.length;


}

/* -----------------------------
Cases CRUD
------------------------------*/

async function createCase(){


const data = {

    title:
        document.getElementById("title").value,

    plaintiff:
        document.getElementById("plaintiff").value,

    defendant:
        document.getElementById("defendant").value,

    facts:
        document.getElementById("facts").value
};

await fetch(`${API}/cases`,{

    method:"POST",

    headers:{
        "Content-Type":"application/json"
    },

    body:JSON.stringify(data)
});

loadCases();


}

async function loadCases(){


const response =
    await fetch(`${API}/cases`);

const cases =
    await response.json();

const tbody =
    document.querySelector("#casesTable tbody");

tbody.innerHTML = "";

cases.forEach(caseItem => {

    tbody.innerHTML += `
    <tr>

        <td>${caseItem.id}</td>

        <td>${caseItem.title}</td>

        <td>${caseItem.plaintiff}</td>

        <td>${caseItem.defendant}</td>

        <td>

            <button
            class="action-btn delete-btn"
            onclick="deleteCase(${caseItem.id})">

                Delete

            </button>

        </td>

    </tr>
    `;
});

loadDashboard();

async function editCase(id){

    const response =
        await fetch(`${API}/cases/${id}`);

    const data =
        await response.json();

    currentCaseId = id;

    document.getElementById("title").value =
        data.title;

    document.getElementById("plaintiff").value =
        data.plaintiff;

    document.getElementById("defendant").value =
        data.defendant;

    document.getElementById("facts").value =
        data.facts;
}


}
async function updateCase(){

    const data = {

        title:
            document.getElementById("title").value,

        plaintiff:
            document.getElementById("plaintiff").value,

        defendant:
            document.getElementById("defendant").value,

        facts:
            document.getElementById("facts").value
    };

    await fetch(

        `${API}/cases/${currentCaseId}`,

        {
            method:"PUT",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(data)
        }
    );

    loadCases();
}
async function deleteCase(id){


await fetch(
    `${API}/cases/${id}`,
    {
        method:"DELETE"
    }
);

loadCases();


}

/* -----------------------------
Templates CRUD
------------------------------*/

async function createTemplate(){


const data = {

    name:
        document.getElementById("templateName").value,

    content:
        document.getElementById("templateContent").value
};

await fetch(`${API}/templates`,{

    method:"POST",

    headers:{
        "Content-Type":"application/json"
    },

    body:JSON.stringify(data)
});

loadTemplates();


}

async function loadTemplates(){


const response =
    await fetch(`${API}/templates`);

const templates =
    await response.json();

const tbody =
    document.querySelector("#templatesTable tbody");

tbody.innerHTML = "";

templates.forEach(template => {

    tbody.innerHTML += `
    <tr>

        <td>${template.id}</td>

        <td>${template.name}</td>

        <td>

            <button
            class="action-btn delete-btn"
            onclick="deleteTemplate(${template.id})">

                Delete

            </button>

        </td>

    </tr>
    `;
});

loadDashboard();


}

async function deleteTemplate(id){


await fetch(
    `${API}/templates/${id}`,
    {
        method:"DELETE"
    }
);

loadTemplates();


}

/* -----------------------------
Upload Documents
------------------------------*/

async function uploadDocument(){


const file =
    document.getElementById("fileInput")
    .files[0];

const formData =
    new FormData();

formData.append(
    "file",
    file
);

const response =
    await fetch(`${API}/upload`,{

        method:"POST",

        body:formData
    });

const result =
    await response.json();

document.getElementById(
    "uploadResult"
).textContent =
    JSON.stringify(
        result,
        null,
        2
    );


}

/* -----------------------------
Generate Draft
------------------------------*/

async function generateDraft(){


const caseId =
    document.getElementById(
        "generateCaseId"
    ).value;

const templateId =
    document.getElementById(
        "generateTemplateId"
    ).value;

const response =
    await fetch(

        `${API}/generate?case_id=${caseId}&template_id=${templateId}`,

        {
            method:"POST"
        }

    );

const result =
    await response.json();

document.getElementById(
    "generatedDraft"
).value =
    result.generated_text;


}

/* -----------------------------
Copy Draft
------------------------------*/

function copyDraft(){


const draft =
    document.getElementById(
        "generatedDraft"
    );

draft.select();

navigator.clipboard.writeText(
    draft.value
);

alert("Draft Copied");


}

/* -----------------------------
Download Draft
------------------------------*/

function downloadDraft(){


const content =
    document.getElementById(
        "generatedDraft"
    ).value;

const blob =
    new Blob(
        [content],
        {type:"text/plain"}
    );

const link =
    document.createElement("a");

link.href =
    URL.createObjectURL(blob);

link.download =
    "yevrah_draft.txt";

link.click();


}

/* -----------------------------
Draft History
------------------------------*/

async function loadDrafts(){


const response =
    await fetch(`${API}/drafts`);

const drafts =
    await response.json();

const tbody =
    document.querySelector("#draftsTable tbody");

tbody.innerHTML = "";

drafts.forEach(draft => {

    tbody.innerHTML += `
    <tr>

        <td>${draft.id}</td>

        <td>${draft.case_id}</td>

        <td>${draft.document_type}</td>

        <td>

            <button
            class="action-btn delete-btn"
            onclick="deleteDraft(${draft.id})">

                Delete

            </button>

        </td>

    </tr>
    `;
});

loadDashboard();


}

async function deleteDraft(id){


await fetch(
    `${API}/draft/${id}`,
    {
        method:"DELETE"
    }
);

loadDrafts();


}

/* -----------------------------
Startup
------------------------------*/

loadCases();
loadTemplates();
loadDrafts();
loadDashboard();
