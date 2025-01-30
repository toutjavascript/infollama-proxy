/***************** SORTING TABLE *****************/
function makeTableSortable() {
  $(".sortable").click(function () {
    const table = $(this).parents("table").eq(0);
    const rows = table
      .find("tr:gt(0)")
      .toArray()
      .sort(comparer($(this).index()));
    this.asc = !this.asc;

    // Update sort indicators
    $(".sortable").removeClass("asc desc");
    $(this).addClass(this.asc ? "asc" : "desc");

    // Sort the rows
    if (!this.asc) {
      rows.reverse();
    }

    // Reattach sorted rows to table
    for (let i = 0; i < rows.length; i++) {
      table.append(rows[i]);
    }
  });
}

function convertValueEndsWithBOrM(value) {
  return value.endsWith("b")
    ? parseFloat(value) * 1e9
    : value.endsWith("m")
    ? parseFloat(value) * 1e6
    : parseFloat(value);
}

function comparer(index) {
  if (index >= 1) {
    /* Because of colspan=2 on header */
    index += 2;
  }
  return function (a, b) {
    const valA = getCellValue(a, index).toLowerCase();
    const valB = getCellValue(b, index).toLowerCase();

    // Check if the values are numbers
    const numA = parseFloat(valA);
    const numB = parseFloat(valB);
    if (!isNaN(numA) && !isNaN(numB)) {
      // Check if string ends with a B or a M
      if (
        (valA.endsWith("b") || valA.endsWith("m")) &&
        (valB.endsWith("b") || valB.endsWith("m"))
      ) {
        // Convert B or M to bytes
        const bytesA = convertValueEndsWithBOrM(valA);
        const bytesB = convertValueEndsWithBOrM(valB);
        return bytesA - bytesB;
      } else {
        if (valA == numA.toString() && valB == numB.toString()) {
          /* Real numbers */
          return numA - numB;
        } else {
          return valA.toString().localeCompare(valB);
        }
      }
    }

    // If not numbers, compare as strings
    return valA.toString().localeCompare(valB);
  };
}

function getCellValue(row, index) {
  const cell = $(row).children("td").eq(index);
  // Check if there's a data-sort attribute
  return cell.attr("data-sort") || cell.text();
}
