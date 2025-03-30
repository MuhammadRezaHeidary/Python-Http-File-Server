document.addEventListener("DOMContentLoaded", function() {
    fetch("/directory")
        .then(response => response.json())
        .then(data => {
            const fileList = document.getElementById("file-list");
            fileList.innerHTML = "";
            
            data.forEach(file => {
                const li = document.createElement("li");
                const link = document.createElement("a");
                link.href = file.is_dir ? `/${file.name}/` : `/${file.name}`;
                link.textContent = file.name;
                link.className = file.is_dir ? "directory" : "file";
                li.appendChild(link);
                fileList.appendChild(li);
            });
        })
        .catch(error => console.error("Error loading files:", error));
});
